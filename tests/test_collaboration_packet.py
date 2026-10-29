"""Synthetic acceptance tests; no live accounts, conversations, or project files."""

from argparse import Namespace
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "packet", Path(__file__).resolve().parents[1] / "scripts" / "collaboration_packet.py"
)
packet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packet)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root / "approved.md"
        self.evidence.write_text("Synthetic evidence only.\n", encoding="utf-8")
        self.args = Namespace(
            output_root=str(self.root / "rounds"), round_id="review-001",
            thread_id="synthetic-thread", request="Review this excerpt only.",
            evidence=[str(self.evidence)], max_bytes=80000,
        )

    def prepared(self):
        return packet.prepare(self.args)

    def response(self):
        return {
            "thread": {"id": "synthetic-thread"},
            "turns": [{
                "id": "synthetic-turn", "status": "completed", "error": None,
                "items": [
                    {"type": "userMessage", "content": [
                        {"type": "text", "text": "ROUND_ID=review-001\nReview only the excerpt."}
                    ]},
                    {"type": "agentMessage", "id": "synthetic-reply", "text": "Synthetic complete reply."},
                ],
            }],
        }

    def receive(self, out, data):
        source = self.root / "private-response.json"
        source.write_text(json.dumps(data), encoding="utf-8")
        return packet.receive(Namespace(round_dir=str(out), thread_json=str(source)))

    def test_prepare_scoped_text_and_refuse_reuse(self):
        out = self.prepared()
        request = (out / "request.md").read_text(encoding="utf-8")
        self.assertIn("Synthetic evidence only.", request)
        self.assertNotIn(str(self.root), request)
        self.assertTrue(request.startswith("ROUND_ID=review-001\n"))
        with self.assertRaises(ValueError):
            self.prepared()

    def test_unsafe_round_id(self):
        self.args.round_id = "../escape"
        with self.assertRaises(ValueError):
            self.prepared()

    def test_invalid_budget(self):
        self.args.max_bytes = 0
        with self.assertRaises(ValueError):
            self.prepared()

    def test_total_request_budget(self):
        self.args.max_bytes = 100
        with self.assertRaises(ValueError):
            self.prepared()
        self.assertFalse((Path(self.args.output_root) / self.args.round_id).exists())

    def test_binary_evidence(self):
        source = self.root / "sample.bin"
        source.write_bytes(b"\x00\xff")
        self.args.evidence = [str(source)]
        with self.assertRaises(ValueError):
            self.prepared()

    def test_complete_reply_and_identical_retry(self):
        out = self.prepared()
        target = self.receive(out, self.response())
        self.assertEqual(target.read_text(encoding="utf-8"), "Synthetic complete reply.\n")
        self.receive(out, self.response())
        receipt = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["reception"], "RECEIVED_COMPLETE")

    def test_wrapped_tool_response(self):
        out = self.prepared()
        data = {"content": [{"type": "text", "text": json.dumps(self.response())}]}
        self.assertTrue(self.receive(out, data).exists())

    def test_wrong_destination(self):
        out = self.prepared()
        data = self.response()
        data["thread"]["id"] = "another-synthetic-thread"
        with self.assertRaises(ValueError):
            self.receive(out, data)

    def test_pending_error_and_truncated(self):
        out = self.prepared()
        for change in ({"status": "in_progress"}, {"error": "synthetic failure"}, {"truncated": True}):
            data = self.response()
            data["turns"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.receive(out, data)
        data = self.response()
        data["turns"][0]["items"][1]["truncated"] = True
        with self.assertRaises(ValueError):
            self.receive(out, data)

    def test_prefix_collision_and_duplicate_turn(self):
        out = self.prepared()
        data = self.response()
        data["turns"][0]["items"][0]["content"][0]["text"] = "ROUND_ID=review-001-extra"
        with self.assertRaises(ValueError):
            self.receive(out, data)
        data = self.response()
        data["turns"].append(copy.deepcopy(data["turns"][0]))
        with self.assertRaises(ValueError):
            self.receive(out, data)

    def test_content_reference_and_empty_answer(self):
        out = self.prepared()
        for text in ('::chatgpt-content-reference{index="0"}', " "):
            data = self.response()
            data["turns"][0]["items"][1]["text"] = text
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.receive(out, data)
        self.assertFalse((out / "web_reply.md").exists())
        receipt = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["reception"], "NOT_RECEIVED")

    def test_different_reply_cannot_overwrite(self):
        out = self.prepared()
        self.receive(out, self.response())
        data = self.response()
        data["turns"][0]["items"][1]["text"] = "A different synthetic reply."
        with self.assertRaises(ValueError):
            self.receive(out, data)


if __name__ == "__main__":
    unittest.main()
