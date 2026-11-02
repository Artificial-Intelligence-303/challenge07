"""Checks on your own run: the server's log in logs/tool-calls.jsonl.

These read the log your agent sessions produced, so they pass only after
you have done the tasks in the README and committed the log.
"""

import json
from pathlib import Path

LOG = Path(__file__).parent.parent / "logs" / "tool-calls.jsonl"


def calls() -> list[dict[str, object]]:
    """Return every logged call, or none if there is no log yet."""
    if not LOG.exists():
        return []
    return [json.loads(line) for line in LOG.read_text().splitlines()]


def results(tool: str) -> list[str]:
    """Return the result of every logged call to one tool."""
    return [str(entry["result"]) for entry in calls() if entry["tool"] == tool]


def test_the_agent_read_the_inbox() -> None:
    """The log holds a list_folder call and a read_email call."""
    assert results("list_folder")
    assert results("read_email")


def test_the_agent_went_past_the_first_page() -> None:
    """The log holds a list_folder call for page 2 or later (task 3)."""
    pages = [
        entry["arguments"]
        for entry in calls()
        if entry["tool"] == "list_folder"
    ]
    assert any(int(str(page.get("page", 1))) >= 2 for page in pages)


def test_the_agent_moved_an_email() -> None:
    """The log holds a move_email call that succeeded."""
    assert any(text.startswith("moved") for text in results("move_email"))


def test_the_agent_sent_a_reply() -> None:
    """The log holds a send_email call that succeeded (task 1)."""
    assert any(text.startswith("sent") for text in results("send_email"))


def test_the_agent_unsubscribed() -> None:
    """The log holds an unsubscribe call that succeeded (task 6)."""
    assert any(not text.startswith("error") for text in results("unsubscribe"))
