import json
from pathlib import Path
from uuid import uuid4

from app.models.schemas import SupportTicket
from app.utils.logger import logger

TICKETS_FILE = Path(__file__).resolve().parents[1] / "data" / "tickets.json"


def _load_tickets() -> list[dict]:
    if not TICKETS_FILE.exists():
        return []
    with TICKETS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _save_tickets(tickets: list[dict]) -> None:
    with TICKETS_FILE.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=2)


def create_support_ticket(
    customer_id: str,
    category: str,
    priority: str,
    description: str,
) -> dict:
    allowed_categories = {"Payment", "Order", "Delivery", "Refund", "Technical"}
    allowed_priorities = {"Low", "Medium", "High"}

    if category not in allowed_categories:
        raise ValueError("Invalid support category.")
    if priority not in allowed_priorities:
        raise ValueError("Invalid priority.")
    if not description.strip():
        raise ValueError("Ticket description cannot be empty.")

    ticket = SupportTicket(
        ticket_id=f"TICKET-{uuid4().hex[:8].upper()}",
        customer_id=customer_id,
        category=category,
        priority=priority,
        description=description.strip(),
    )

    tickets = _load_tickets()
    tickets.append(ticket.model_dump())
    _save_tickets(tickets)

    logger.info(
        "Tool create_support_ticket succeeded ticket=%s category=%s priority=%s",
        ticket.ticket_id,
        ticket.category,
        ticket.priority,
    )
    return ticket.model_dump()
