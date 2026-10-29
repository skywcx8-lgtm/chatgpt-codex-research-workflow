"""Prepare scoped text requests and validate replies; no transport or execution."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re


TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".inp", ".log", ".py"}
REFERENCE_MARKER = "::chatgpt-content-reference"


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(args):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", args.round_id):
        raise ValueError("Unsafe round ID")
    if not args.thread_id.strip() or not args.request.strip():
        raise ValueError("Destination and request must not be empty")
    if args.max_bytes <= 0:
        raise ValueError("Text budget must be positive")
    out = Path(args.output_root).resolve() / args.round_id
    if out.exists():
        raise ValueError("Round already exists; refusing to overwrite")
    parts = [f"ROUND_ID={args.round_id}", args.request]
    sources = []
    for name in args.evidence:
        path = Path(name).resolve(strict=True)
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError("Evidence must be a supported UTF-8 text file")
        if path.stat().st_size > args.max_bytes:
            raise ValueError("Evidence too large; extract a scoped excerpt first")
        content = path.read_text(encoding="utf-8-sig")
        parts.append(f"--- Evidence: {path.name} ---\n{content}")
        sources.append(str(path))
    parts.append("Base the answer on the supplied evidence. Distinguish observations, inferences, and recommendations; do not execute local tasks.")
    request = "\n\n".join(parts) + "\n"
    if len(request.encode("utf-8")) > args.max_bytes:
        raise ValueError("Combined request exceeds text budget")
    out.mkdir(parents=True)
    (out / "request.md").write_text(request, encoding="utf-8")
    write_json(out / "receipt.json", {
        "round_id": args.round_id,
        "destination_thread_id": args.thread_id,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "sources_included": sources,
        "dispatch": "NOT_SENT",
        "reception": "NOT_RECEIVED",
    })
    return out


def unwrap_response(data):
    if not isinstance(data, dict):
        raise ValueError("Expected a read_thread JSON object")
    if "turns" not in data and "content" in data:
        blocks = [block.get("text", "") for block in data["content"] if block.get("type") == "text"]
        if len(blocks) != 1:
            raise ValueError("Expected one read_thread JSON text block")
        data = json.loads(blocks[0])
    if not isinstance(data, dict):
        raise ValueError("Expected a read_thread JSON object")
    return data


def receive(args):
    out = Path(args.round_dir).resolve(strict=True)
    receipt_path = out / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    data = unwrap_response(json.loads(Path(args.thread_json).read_text(encoding="utf-8-sig")))
    if data.get("thread", {}).get("id") != receipt["destination_thread_id"]:
        raise ValueError("Wrong destination thread")
    marker = re.compile(r"^ROUND_ID=" + re.escape(receipt["round_id"]) + r"\s*$", re.MULTILINE)
    matches = []
    for turn in data.get("turns", []):
        user_text = "\n".join(
            block.get("text", "")
            for item in turn.get("items", []) if item.get("type") == "userMessage"
            for block in item.get("content", []) if block.get("type") == "text"
        )
        if marker.search(user_text):
            matches.append(turn)
    if len(matches) != 1:
        raise ValueError("Expected exactly one matching round turn; reply pending or ambiguous")
    turn = matches[0]
    if turn.get("status") != "completed" or turn.get("error"):
        raise ValueError("Matching turn not successfully completed")
    replies = [item for item in turn.get("items", []) if item.get("type") == "agentMessage"]
    if turn.get("truncated") or not replies or any(item.get("truncated") for item in replies):
        raise ValueError("Missing or truncated reply; retrieve the full answer first")
    texts = [item.get("text", "") for item in replies]
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("Missing reply text")
    answer = "\n\n".join(texts).strip()
    if REFERENCE_MARKER in answer:
        raise ValueError("Content-reference placeholder; retrieve the actual answer first")
    target = out / "web_reply.md"
    if target.exists() and target.read_text(encoding="utf-8") != answer + "\n":
        raise ValueError("Refusing to overwrite a different received reply")
    target.write_text(answer + "\n", encoding="utf-8")
    receipt.update(
        dispatch="CONFIRMED_BY_MATCHING_TURN",
        reception="RECEIVED_COMPLETE",
        response_turn_id=turn["id"],
        response_message_ids=[item["id"] for item in replies if item.get("id")],
        web_reply_path=str(target),
        received_at=datetime.now(timezone.utc).isoformat(),
    )
    write_json(receipt_path, receipt)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--output-root", required=True)
    prep.add_argument("--round-id", required=True)
    prep.add_argument("--thread-id", required=True)
    prep.add_argument("--request", required=True)
    prep.add_argument("--evidence", action="append", default=[])
    prep.add_argument("--max-bytes", type=int, default=80000)
    rec = sub.add_parser("receive")
    rec.add_argument("--round-dir", required=True)
    rec.add_argument("--thread-json", required=True)
    args = parser.parse_args()
    try:
        print((prepare if args.command == "prepare" else receive)(args))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
