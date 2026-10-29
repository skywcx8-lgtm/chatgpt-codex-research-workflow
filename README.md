# ChatGPT–Codex Research Workflow

一个仅在明确调用时启用的 Codex Skill：让 Codex 与用户指定的 ChatGPT 网页对话协作，核对真实回包，并按授权继续本地工作。

An explicitly invoked Codex skill for scoped collaboration with a user-selected ChatGPT conversation. It verifies actual replies and can use an independently configured shared-workspace connector.

## 它做什么 / Scope

- 精确选择目标对话和账号/Profile，不沿用其他项目的默认目标。
- 使用实际可用的对话工具或受支持的浏览器界面；发送一次并匹配本轮回复。
- 可选使用已有 MCP 文件连接，核对根目录和实际文件内容。
- 两边都可分析、编程、写作和 Review；简单本地任务不必绕行网页。
- `policy.allow_implicit_invocation: false`：只在明确调用时启用。

This is **not** an MCP server, tunnel, OAuth implementation, browser extension, or autonomous multi-agent framework. It does not provision accounts or network access.

## 安装 / Installation

Clone this repository into a skill directory supported by your Codex installation. For the common user-level layout, use a new, non-existing destination:

```sh
git clone https://github.com/skywcx8-lgtm/chatgpt-codex-research-workflow.git ~/.codex/skills/chatgpt-codex-research-workflow
```

Windows PowerShell:

```powershell
git clone https://github.com/skywcx8-lgtm/chatgpt-codex-research-workflow.git "$env:USERPROFILE\.codex\skills\chatgpt-codex-research-workflow"
```

If the destination already exists, inspect it before merging or replacing anything. An installation using a different skill root should use that configured root. Start a new Codex session if necessary for discovery.

## 使用 / Usage

在 Codex 中明确调用，并提供真实目标和范围：

```text
使用 $chatgpt-codex-research-workflow。
目标 ChatGPT 对话：<由我提供的对话链接>
只使用我指定的账号和浏览器 Profile。
请对我授权的测试材料进行只读分析，取回本轮完整回复。
本轮不修改文件、不执行求解器、不访问其他目录。
```

网页端直接使用文件连接时，应在网页中选择自己配置的 App；无需先调用 Codex Skill。安装本技能不会自动获得本地文件访问权限。

For a live file bridge, separately configure an appropriate MCP workspace server and authentication. An existing implementation such as [coding-tools-mcp-workbench](https://github.com/biaobiao2233/coding-tools-mcp-workbench) may be used; this repository does not bundle or modify it. Verify the server's actual path and command restrictions rather than assuming the working directory is a security boundary.

## Optional text packet helper

Python 3.10+; standard library only. No network access or external command execution is implemented by the helper.

```sh
python scripts/collaboration_packet.py prepare --output-root ./private-rounds --round-id review-001 --thread-id THREAD_ID --request "Review only the approved excerpt." --evidence ./approved-excerpt.md
python scripts/collaboration_packet.py receive --round-dir ./private-rounds/review-001 --thread-json ./private-thread-response.json
```

Review `request.md` before sending it through your available conversation tool. The helper does **not** send it. Export that tool's actual `read_thread` JSON to a private file for `receive`. Content-reference placeholders, wrong destinations, incomplete turns, and truncated replies are rejected.

The helper is not a credential detector or anonymizer. Evidence may contain confidential text: only include material authorized for the selected destination. Keep generated packets, receipts, replies, and exported conversation JSON out of public repositories. Runtime receipts can contain local source paths.

## Verification and limits

```sh
python -m unittest discover -s tests -v
```

Tests use synthetic data and temporary folders; they do not log in, message real conversations, access an MCP server, or launch a solver. Native conversation tools may be unavailable in other installations. The published package does not guarantee a subscription tier, write capability, uptime, or restart recovery. Test those capabilities separately in an isolated workspace.

## Privacy

This distribution contains reusable instructions, a local helper, and synthetic tests only. It includes no live endpoint, token, browser profile identifier, conversation ID, private filesystem path, research model, or research data. Configure deployment settings privately outside this repository.
