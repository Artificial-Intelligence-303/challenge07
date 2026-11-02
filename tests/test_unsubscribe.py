"""What task 6 asks the agent to build: an unsubscribe tool.

These fail until the agent has added it. You do not write the code; you
check that what the agent wrote makes these pass.
"""

import json

from helpers import call, tools

import server

LIBRARY = "updates@library.hilltop.edu"


def test_the_server_offers_unsubscribe() -> None:
    """Unsubscribe is on offer alongside the other tools."""
    assert "unsubscribe" in tools()


def test_unsubscribe_archives_that_sender_only() -> None:
    """The library's inbox emails go to archive; nothing else moves.

    Email 6, from the library, is moved to important first: unsubscribe
    leaves it there, since it only clears the inbox.
    """
    call("move_email", email_id=6, folder="important")
    result = call("unsubscribe", sender=LIBRARY)
    assert not result.startswith("error")
    archive = call("list_folder", folder="archive", page=1)
    assert archive.count("Library Updates") == 2
    assert "Campus Weekly" not in archive
    assert "Jordan" not in archive
    assert "#6 |" in call("list_folder", folder="important", page=1)
    inbox_pages = [
        call("list_folder", folder="inbox", page=page) for page in (1, 2)
    ]
    assert all("Library Updates" not in page for page in inbox_pages)


def test_unsubscribing_from_a_stranger_is_an_error_result() -> None:
    """No email comes from this address, so there is nothing to do."""
    assert call("unsubscribe", sender="nobody@nowhere.example").startswith(
        "error"
    )


def test_an_unsubscribe_is_logged() -> None:
    """The server's log records the unsubscribe call."""
    call("unsubscribe", sender=LIBRARY)
    last = json.loads(server.LOG.read_text().splitlines()[-1])
    assert last["tool"] == "unsubscribe"
