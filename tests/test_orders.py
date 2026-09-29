import pytest

from app.tools.order_tools import get_order_details, get_order_status


def test_get_order_status_for_owner():
    result = get_order_status("ORD-1005", "CUS-002")
    assert result["status"] == "Out for Delivery"


def test_get_order_details_for_owner():
    result = get_order_details("ORD-1001", "CUS-001")
    assert result["restaurant"] == "Food Palace"


def test_wrong_customer_is_blocked():
    with pytest.raises(PermissionError):
        get_order_status("ORD-1005", "CUS-001")


def test_invalid_order_id():
    with pytest.raises(ValueError):
        get_order_status("ABC-999", "CUS-001")


def test_missing_order():
    with pytest.raises(LookupError):
        get_order_status("ORD-9999", "CUS-001")
