from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(default="default", min_length=1, max_length=100)


class ChatResponse(BaseModel):
    session_id: str
    response: str
    tool_calls: list[str] = []
    sources: list[str] = []


class SupportTicketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1, max_length=50)
    category: Literal["Payment", "Order", "Delivery", "Refund", "Technical"]
    priority: Literal["Low", "Medium", "High"]
    description: str = Field(min_length=5, max_length=2000)


class ComplaintClassification(BaseModel):
    category: Literal["Payment", "Order", "Delivery", "Refund", "Technical"]
    priority: Literal["Low", "Medium", "High"]
    sentiment: Literal["Positive", "Neutral", "Negative"]
    reason: str = Field(min_length=1, max_length=500)


class Order(BaseModel):
    order_id: str
    customer_id: str
    restaurant: str
    items: list[str]
    total: float
    status: str
    estimated_delivery: str


class SupportTicket(BaseModel):
    ticket_id: str
    customer_id: str
    category: Literal["Payment", "Order", "Delivery", "Refund", "Technical"]
    priority: Literal["Low", "Medium", "High"]
    description: str
    status: Literal["Open", "In Progress", "Resolved"] = "Open"
