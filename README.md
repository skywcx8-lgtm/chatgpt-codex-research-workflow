# ChatGPT–Codex Research Workflow

[English](#english) | [简体中文](#简体中文)

## English

An explicitly invoked Codex skill for collaboration with a user-selected ChatGPT conversation. It sends only authorized evidence, verifies the matching completed reply, and supports continued local work within the user's scope. An independently configured shared-workspace connector can provide direct file access.

### Features

- Select the exact conversation, account, and browser profile instead of reusing another project's destination.
- Use available conversation tools or a supported browser interface; send once and match the reply to the current round.
- Optionally use an existing MCP file connector, verifying its workspace and actual file contents.
- Let either side analyze, code, write, and review. Complete simple local tasks directly when a web round trip adds no value.
- Invoke explicitly: `policy.allow_implicit_invocation: false`.

This is a collaboration skill, **not** an MCP server, tunnel, OAuth implementation, browser extension, or autonomous multi-agent framework. It does not provision accounts or network access.

### Installation

Clone this repository into a skill directory supported by your Codex installation. For the common user-level layout, use a new, non-existing destination:

```sh
git clone https://github.com/skywcx8-lgtm/chatgpt-codex-research-workflow.git ~/.codex/skills/chatgpt-codex-research-workflow
```

Windows PowerShell:

```powershell
git clone https://github.com/skywcx8-lgtm/chatgpt-codex-research-workflow.git "$env:USERPROFILE\.codex\skills\chatgpt-codex-research-workflow"
```

If the destination already exists, inspect it before merging or replacing anything. If your installation uses a different skill root, use that configured root. Start a new Codex session if necessary for discovery.

### Usage

Explicitly invoke the skill in Codex and specify the destination and scope:

```text
Use $chatgpt-codex-research-workflow.
Target ChatGPT conversation: <conversation link supplied by me>
Use only my selected account and browser profile.
Perform a read-only analysis of the test materials I authorize and retrieve the complete reply for this round.
Do not modify files, run a solver, or access other directories in this round.
```

To use a file connector directly in ChatGPT web, select your configured App there; invoking this Codex skill first is unnecessary. Installing the skill does not grant access to local files.

For a live file bridge, separately configure an appropriate MCP workspace server and authentication. An existing implementation such as [coding-tools-mcp-workbench](https://github.com/biaobiao2233/coding-tools-mcp-workbench) may be used; this repository does not bundle or modify it. Verify the server's actual path and command restrictions rather than assuming the working directory is a security boundary.

### Optional text packet helper

Requires Python 3.10+ and the standard library only. The helper does not access the network or execute external commands.

```sh
python scripts/collaboration_packet.py prepare --output-root ./private-rounds --round-id review-001 --thread-id THREAD_ID --request "Review only the approved excerpt." --evidence ./approved-excerpt.md
python scripts/collaboration_packet.py receive --round-dir ./private-rounds/review-001 --thread-json ./private-thread-response.json
```

Review `request.md` before sending it through your available conversation tool. The helper does **not** send it. Export that tool's actual `read_thread` JSON to a private file for `receive`. Content-reference placeholders, wrong destinations, incomplete turns, and truncated replies are rejected.

The helper is not a credential detector or anonymizer. Include only evidence authorized for the selected destination. Keep generated packets, receipts, replies, and exported conversation JSON out of public repositories. Runtime receipts can contain local source paths.

### Verification and limits

```sh
python -m unittest discover -s tests -v
```

Tests use synthetic data and temporary folders; they do not log in, message real conversations, access an MCP server, or launch a solver. Native conversation tools may be unavailable in other installations. The published package does not guarantee a subscription tier, write capability, uptime, or restart recovery. Test those capabilities separately in an isolated workspace.

### Privacy

This distribution contains reusable instructions, a local helper, and synthetic tests only. It includes no live endpoint, token, browser profile identifier, conversation ID, private filesystem path, research model, or research data. Configure deployment settings privately outside this repository.

## 简体中文

这是一个仅在明确调用时启用的 Codex 技能，用于与用户指定的 ChatGPT 对话协作：只发送已授权的材料，核对本轮完整回复，并在用户授权范围内继续本地工作。单独配置的共享 Workspace 连接可提供直接文件访问能力。

### 功能

- 精确选择目标对话、账号和浏览器 Profile，不沿用其他项目的默认目标。
- 使用实际可用的对话工具或受支持的浏览器界面；发送一次，并匹配本轮回复。
- 可选使用已有 MCP 文件连接，核对 Workspace 和实际文件内容。
- 两边都可分析、编程、写作和 Review；简单本地任务直接完成，不为协作而增加网页交接。
- 仅显式调用：`policy.allow_implicit_invocation: false`。

这是协作技能，**不是** MCP 服务器、Tunnel、OAuth 实现、浏览器扩展或自主多智能体框架，不负责创建账号或开通网络访问。

### 安装

将仓库克隆到当前 Codex 支持的技能目录。对于常见的用户级目录，使用一个尚不存在的新目标目录：

```sh
git clone https://github.com/skywcx8-lgtm/chatgpt-codex-research-workflow.git ~/.codex/skills/chatgpt-codex-research-workflow
```

Windows PowerShell：

```powershell
git clone https://github.com/skywcx8-lgtm/chatgpt-codex-research-workflow.git "$env:USERPROFILE\.codex\skills\chatgpt-codex-research-workflow"
```

如果目标目录已存在，先检查内容，再决定是否合并或替换。若当前安装使用其他技能根目录，请采用实际配置的目录；必要时新建 Codex 会话以发现技能。

### 使用

在 Codex 中明确调用，并指定目标和范围：

```text
使用 $chatgpt-codex-research-workflow。
目标 ChatGPT 对话：<由我提供的对话链接>
只使用我指定的账号和浏览器 Profile。
请对我授权的测试材料进行只读分析，取回本轮完整回复。
本轮不修改文件、不执行求解器、不访问其他目录。
```

如果只想在 ChatGPT 网页端直接使用文件连接，在网页中选择自己配置的 App 即可，无需先调用 Codex 技能。安装本技能不会自动获得本地文件访问权限。

如需实时文件桥接，应另行配置合适的 MCP Workspace 服务器和身份验证。可采用 [coding-tools-mcp-workbench](https://github.com/biaobiao2233/coding-tools-mcp-workbench) 等已有实现；本仓库不打包或修改该项目。应核实服务器实际的路径和命令限制，不能假定工作目录就是文件系统的安全边界。

### 可选的文本协作包辅助脚本

需要 Python 3.10+，仅使用标准库。辅助脚本不联网，也不执行外部命令。

```sh
python scripts/collaboration_packet.py prepare --output-root ./private-rounds --round-id review-001 --thread-id THREAD_ID --request "Review only the approved excerpt." --evidence ./approved-excerpt.md
python scripts/collaboration_packet.py receive --round-dir ./private-rounds/review-001 --thread-json ./private-thread-response.json
```

通过可用的对话工具发送前，请先检查 `request.md`；辅助脚本**不会代发**。将工具实际返回的 `read_thread` JSON 导出到私有文件，再交给 `receive`。脚本会拒绝内容引用占位符、错误目标、未完成的对话轮次和被截断的回复。

辅助脚本不是凭据检测器或匿名化工具。只应包含已获准发送给指定目标的材料。生成的协作包、回执、回复和导出的对话 JSON 都不应进入公开仓库；运行时回执可能包含本地源文件路径。

### 验证与限制

```sh
python -m unittest discover -s tests -v
```

测试只使用合成数据和临时目录，不登录账号、不向真实对话发消息、不访问 MCP 服务器，也不启动求解器。其他安装环境可能没有原生对话工具。本技能不保证特定套餐权限、写入能力、服务在线率或重启恢复；这些能力需在隔离 Workspace 中分别实测。

### 隐私

发布包仅包含可复用说明、本地辅助脚本和合成测试，不包含真实部署地址、Token、浏览器 Profile 标识、对话 ID、私人文件路径、科研模型或科研数据。部署配置应单独保存在本仓库之外的私有位置。
