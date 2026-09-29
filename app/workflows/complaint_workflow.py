from app.models.schemas import ComplaintClassification
from app.tools.support_tools import create_support_ticket
from app.utils.logger import logger


def apply_business_rules(classification: ComplaintClassification) -> ComplaintClassification:
    """
    Application-side rules can override unsafe/weak model priorities.
    The LLM does not get the final say on business-critical behavior.
    """
    priority = classification.priority

    if classification.category == "Payment" and classification.sentiment == "Negative":
        priority = "High"

    return classification.model_copy(update={"priority": priority})


def run_complaint_workflow(
    customer_id: str,
    classification: ComplaintClassification,
    description: str,
) -> dict:
    classification = apply_business_rules(classification)

    ticket = create_support_ticket(
        customer_id=customer_id,
        category=classification.category,
        priority=classification.priority,
        description=description,
    )

    result = {
        "classification": classification.model_dump(),
        "ticket": ticket,
    }

    logger.info(
        "Complaint workflow completed ticket=%s",
        ticket["ticket_id"],
    )
    return result
