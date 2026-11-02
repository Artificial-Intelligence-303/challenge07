"""Checks on the provided tools. These pass before you start.

If one fails after task 6, the agent's change broke something that
worked: read the test, then ask the agent to fix it, or restore a
checkpoint.
"""

import json

from helpers import call, tools

import mail
import server


def test_the_server_offers_the_five_tools() -> None:
    """list_folder, read_email, move_email, draft_reply, send_email."""
    names = tools()
    for name in (
        "list_folder",
        "read_email",
        "move_email",
        "draft_reply",
        "send_email",
    ):
        assert name in names


def test_the_tools_say_what_kind_they_are() -> None:
    """Reading is marked read-only; sending is marked as not undoable."""
    offered = tools()
    assert offered["list_folder"].annotations.read_only_hint
    assert offered["read_email"].annotations.read_only_hint
    assert not offered["move_email"].annotations.read_only_hint
    assert offered["send_email"].annotations.destructive_hint


def test_the_inbox_comes_in_pages() -> None:
    """Twenty-two emails, eight a page: page 3 is the last."""
    first = call("list_folder", folder="inbox", page=1)
    assert "page 1 of 3" in first
    assert "more on page 2" in first
    last = call("list_folder", folder="inbox", page=3)
    assert "page 3 of 3" in last
    assert "more on page" not in last


def test_read_email_shows_the_body() -> None:
    """Email 2 is Jordan asking about Thursday."""
    result = call("read_email", email_id=2)
    assert "Jordan" in result
    assert "Thursday" in result


def test_a_moved_email_changes_folder() -> None:
    """Email 5 moved to spam is no longer in the inbox."""
    assert call("move_email", email_id=5, folder="spam").startswith("moved")
    assert "#5 |" not in call("list_folder", folder="inbox", page=1)
    assert "#5 |" in call("list_folder", folder="spam", page=1)


def test_a_missing_email_is_an_error_result() -> None:
    """Reading an email that does not exist returns an error message."""
    assert call("read_email", email_id=99).startswith("error")


def test_a_sent_email_lands_in_sent() -> None:
    """send_email adds the message to the sent folder."""
    result = call(
        "send_email",
        to="jordan.lee@hilltop.edu",
        subject="Hi",
        body="Thursday works.",
    )
    assert result.startswith("sent")
    assert "Hi" in call("list_folder", folder="sent", page=1)


def test_every_call_is_logged() -> None:
    """Two calls give two log lines, with tool, arguments and result."""
    call("list_folder", folder="inbox", page=2)
    call("move_email", email_id=99, folder="spam")
    lines = server.LOG.read_text().splitlines()
    assert len(lines) == 2
    second = json.loads(lines[1])
    assert second["tool"] == "move_email"
    assert second["arguments"] == {"email_id": 99, "folder": "spam"}
    assert second["result"].startswith("error")


def test_the_mailbox_starts_untouched() -> None:
    """Nothing is in sent or drafts before any session."""
    start = mail.starting_mailbox()["emails"]
    assert all(email["folder"] == "inbox" for email in start)
