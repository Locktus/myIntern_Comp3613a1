from types import SimpleNamespace
from app.utilities.pagination import Pagination
from app.utilities.flash import flash, get_flashed_messages


def test_ut_06_pagination():
    """UT-06: Pagination calculates pages and flags."""
    page = Pagination(25, 2, 10)
    assert page.total_pages == 3 and page.has_prev and page.has_next


def test_ut_07_flash_messages():
    """UT-07: Flash messages are stored and consumed."""
    request = SimpleNamespace(session={})
    flash(request, "hello", "warning")
    assert get_flashed_messages(request) == [{"message": "hello", "type": "warning"}]
    assert get_flashed_messages(request) == []
