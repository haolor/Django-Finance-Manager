"""AI / NLP microservice — Gemini + NLP; calls Core API for data writes."""
from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .config import settings
from .core_client import CoreClient
from .gemini_client import get_chat_response, predict_next_month_spending_with_ai
from .nlp_service import NLPService

app = FastAPI(title="Finance AI/NLP Service", version="1.0.0")


def get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    auth = authorization.strip()
    if auth.lower().startswith("token "):
        return auth[6:].strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return auth


class ChatBody(BaseModel):
    message: str = Field(..., min_length=1)


class ParseTransactionBody(BaseModel):
    text: str = Field(..., min_length=1)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-nlp"}


@app.post("/v1/chat")
def chat(body: ChatBody, token: str = Depends(get_token)):
    core = CoreClient()
    try:
        ctx = core.get_finance_context(token)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Core finance-context failed: {exc}") from exc
    try:
        reply = get_chat_response(ctx, body.message)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini error: {exc}") from exc
    return {
        "message": body.message,
        "response": reply,
        "provider": "gemini",
        "model": settings.gemini_model,
    }


@app.get("/v1/predictions")
def predictions_gemini(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    token: str = Depends(get_token),
):
    core = CoreClient()
    try:
        ctx = core.get_finance_context(token, start_date=start_date, end_date=end_date)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Core finance-context failed: {exc}") from exc
    try:
        return predict_next_month_spending_with_ai(ctx)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        try:
            return core.get_local_predictions(token, start_date=start_date, end_date=end_date)
        except Exception as exc2:
            raise HTTPException(status_code=502, detail=str(exc2)) from exc2


@app.post("/v1/parse-transaction")
def parse_transaction(body: ParseTransactionBody, token: str = Depends(get_token)):
    nlp_result = NLPService.extract_transaction_info(body.text)
    if not nlp_result.get("amount"):
        raise HTTPException(
            status_code=400,
            detail="Could not extract amount from text. Example: 'Chi 50k ăn sáng'",
        )
    core = CoreClient()
    category_id = None
    if nlp_result.get("category"):
        try:
            category_id = core.ensure_category_id(
                token, nlp_result["category"], nlp_result.get("type", "expense")
            )
        except Exception:
            category_id = None
    td: date = nlp_result["date"]
    try:
        tx = core.create_transaction(
            token,
            category_id=category_id,
            amount=nlp_result["amount"],
            description=str(nlp_result.get("description") or ""),
            transaction_date=td,
            original_nlp_input=body.text,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Core create transaction failed: {exc}") from exc
    def _ser(v):
        if hasattr(v, "isoformat"):
            return v.isoformat()
        if hasattr(v, "__float__") and not isinstance(v, bool):
            return float(v)
        return v

    return {"transaction": tx, "nlp": {k: _ser(v) for k, v in nlp_result.items()}}
