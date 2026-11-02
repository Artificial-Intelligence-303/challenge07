"""An MCP server that offers a mailbox's tools to any agent.

Provided. VS Code starts it from `.vscode/mcp.json`. It never talks to a
model: an agent's program asks it for its list of tools, then sends it the
calls the model makes, and it sends back each result.

Every call it receives is added to `logs/tool-calls.jsonl`, one line per
call: the tool, its arguments and the result. `uv run python src/main.py
log` prints that file as a transcript. A call that is declined in VS Code
does not reach this server, so it is not logged.

Each tool's annotations tell the agent's program what kind of tool it is:
`read_only_hint` for one that changes nothing, `destructive_hint` for one
whose effect cannot be undone.
"""

import datetime
import json
from collections.abc import Callable
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

import mail

LOG = Path(__file__).parent.parent / "logs" / "tool-calls.jsonl"

server = MCPServer(
    "inbox",
    instructions="Read, sort and answer email for the mailbox owner.",
)

READ_ONLY = ToolAnnotations(read_only_hint=True)
CHANGES = ToolAnnotations(read_only_hint=False, destructive_hint=False)
CANNOT_UNDO = ToolAnnotations(read_only_hint=False, destructive_hint=True)


def run(
    tool: str, arguments: dict[str, object], work: Callable[[], str]
) -> str:
    """Run one tool call, log it, and return its result as text.

    A ValueError comes back as a result starting "error:", so the model
    can read what went wrong and try again.
    """
    try:
        result = work()
    except ValueError as problem:
        result = f"error: {problem}"
    entry = {
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "tool": tool,
        "arguments": arguments,
        "result": result,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as log:
        log.write(json.dumps(entry) + "\n")
    return result


@server.tool(annotations=READ_ONLY)
def list_folder(folder: str = "inbox", page: int = 1) -> str:
    """List one page of a mail folder, newest first, eight emails a page.

    The folders are inbox, important, archive, spam, drafts and sent.
    """
    return run(
        "list_folder",
        {"folder": folder, "page": page},
        lambda: mail.list_folder(folder, page, mail.DATA),
    )


@server.tool(annotations=READ_ONLY)
def read_email(email_id: int) -> str:
    """Read one email in full, by the id that list_folder shows."""
    return run(
        "read_email",
        {"email_id": email_id},
        lambda: mail.read_email(email_id, mail.DATA),
    )


@server.tool(annotations=CHANGES)
def move_email(email_id: int, folder: str) -> str:
    """Move one email to inbox, important, archive or spam."""
    return run(
        "move_email",
        {"email_id": email_id, "folder": folder},
        lambda: mail.move_email(email_id, folder, mail.DATA),
    )


@server.tool(annotations=CHANGES)
def draft_reply(email_id: int, body: str) -> str:
    """Save a reply to one email in drafts. Nothing is sent."""
    return run(
        "draft_reply",
        {"email_id": email_id, "body": body},
        lambda: mail.draft_reply(email_id, body, mail.DATA),
    )


@server.tool(annotations=CANNOT_UNDO)
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email from the mailbox owner. It cannot be taken back."""
    return run(
        "send_email",
        {"to": to, "subject": subject, "body": body},
        lambda: mail.send_email(to, subject, body, mail.DATA),
    )


if __name__ == "__main__":
    server.run()
