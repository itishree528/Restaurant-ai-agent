import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from openai import OpenAI

from app.agent.graph import RestaurantAgent
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ComplaintClassification,
    SupportTicketRequest,
)
from app.rag.retriever import KnowledgeRetriever
from app.tools.order_tools import get_order_details, get_order_status
from app.tools.support_tools import create_support_ticket
from app.workflows.complaint_workflow import run_complaint_workflow
from app.utils.logger import logger

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "rag" / "documents"

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-5")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Create a .env file from .env.example."
    )

client = OpenAI(api_key=api_key)
retriever = KnowledgeRetriever(DOCUMENTS_DIR)
agent = RestaurantAgent(client=client, retriever=retriever, model=model)

app = FastAPI(
    title="AI Restaurant Support & Operations Agent",
    version="1.0.0",
    description="Technical assessment project for AI automation and agents.",
)


@app.get("/")
def root():
    return {
        "name": "AI Restaurant Support & Operations Agent",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": model,
        "knowledge_documents": len(retriever.documents),
    }


@app.get("/api/orders/{order_id}")
def order_details(order_id: str, customer_id: str):
    try:
        return get_order_details(order_id, customer_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/orders/{order_id}/status")
def order_status(order_id: str, customer_id: str):
    try:
        return get_order_status(order_id, customer_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/api/support/tickets")
def support_ticket(request: SupportTicketRequest):
    try:
        return create_support_ticket(
            customer_id=request.customer_id,
            category=request.category,
            priority=request.priority,
            description=request.description,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/agent/chat", response_model=ChatResponse)
def agent_chat(request: ChatRequest):
    try:
        result = agent.chat(
            customer_id=request.customer_id,
            session_id=request.session_id,
            message=request.message,
        )

        return ChatResponse(
            session_id=request.session_id,
            response=result["response"],
            tool_calls=result["tool_calls"],
            sources=result["sources"],
        )

    except Exception:
        logger.exception("Agent request failed")
        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable.",
        )


@app.post("/api/agent/classify-complaint", response_model=ComplaintClassification)
def classify_complaint(request: ChatRequest):
    try:
        return agent.classify_complaint(request.message)
    except Exception:
        logger.exception("Complaint classification failed")
        raise HTTPException(
            status_code=503,
            detail="Complaint classification is temporarily unavailable.",
        )


@app.post("/api/agent/complaint-workflow")
def complaint_workflow(request: ChatRequest):
    try:
        classification = agent.classify_complaint(request.message)

        result = run_complaint_workflow(
            customer_id=request.customer_id,
            classification=classification,
            description=request.message,
        )

        return result

    except Exception:
        logger.exception("Complaint workflow failed")
        raise HTTPException(
            status_code=503,
            detail="Complaint workflow is temporarily unavailable.",
        )
