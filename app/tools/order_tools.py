import json
import re
from pathlib import Path
from app.models.schemas import Order
from app.utils.logger import logger

ORDER_ID_PATTERN = re.compile(r"^ORD-\d{4}$")
ORDERS_FILE = Path(__file__).resolve().parents[1] / "data" / "orders.json"


def _load_orders() -> list[Order]:
    with ORDERS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return [Order.model_validate(item) for item in data]


def _validate_order_id(order_id: str) -> None:
    if not ORDER_ID_PATTERN.fullmatch(order_id):
        raise ValueError("Invalid order ID format. Expected ORD-1234.")


def _get_customer_order(order_id: str, customer_id: str) -> Order:
    _validate_order_id(order_id)

    for order in _load_orders():
        if order.order_id == order_id:
            if order.customer_id != customer_id:
                raise PermissionError(
                    "You are not authorized to access this order."
                )
            return order

    raise LookupError("Order not found.")


def get_order_status(order_id: str, customer_id: str) -> dict:
    """Return the authoritative current status for the authenticated customer's order."""
    order = _get_customer_order(order_id, customer_id)
    logger.info("Tool get_order_status succeeded for order=%s", order_id)
    return {
        "order_id": order.order_id,
        "status": order.status,
        "estimated_delivery": order.estimated_delivery,
    }


def get_order_details(order_id: str, customer_id: str) -> dict:
    """Return authoritative details for the authenticated customer's order."""
    order = _get_customer_order(order_id, customer_id)
    logger.info("Tool get_order_details succeeded for order=%s", order_id)
    return order.model_dump()
