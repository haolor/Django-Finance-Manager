"""
Gemini service for AI chat responses and predictions.
"""
import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Sum

from .models import Transaction


class GeminiService:
    """Service call Google Gemini model via Generative Language API."""

    DEFAULT_MODEL = "gemini-3-flash-preview"
    API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    DEFAULT_TIMEOUT_SECONDS = 60
    DEFAULT_MAX_OUTPUT_TOKENS = 1200
    MAX_CONTINUATION_CALLS = 1

    @staticmethod
    def _get_api_key() -> str:
        return (getattr(settings, "GEMINI_API_KEY", "") or "").strip()

    @staticmethod
    def _call_generate_content(system_prompt: str, user_prompt: str) -> str:
        api_key = GeminiService._get_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        model = getattr(settings, "GEMINI_MODEL", GeminiService.DEFAULT_MODEL)
        api_url = GeminiService.API_URL_TEMPLATE.format(model=model, api_key=api_key)

        timeout_seconds = int(
            getattr(settings, "GEMINI_TIMEOUT_SECONDS", GeminiService.DEFAULT_TIMEOUT_SECONDS)
        )
        max_output_tokens = int(
            getattr(settings, "GEMINI_MAX_OUTPUT_TOKENS", GeminiService.DEFAULT_MAX_OUTPUT_TOKENS)
        )

        combined_text = ""
        current_prompt = user_prompt

        for _ in range(GeminiService.MAX_CONTINUATION_CALLS + 1):
            payload = {
                "systemInstruction": {
                    "parts": [{"text": system_prompt}],
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": current_prompt}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": max_output_tokens,
                },
            }

            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                method="POST",
                headers={
                    "Content-Type": "application/json",
                },
            )

            try:
                with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                    data = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="ignore")
                raise RuntimeError(f"Gemini HTTPError {exc.code}: {detail}") from exc
            except urllib.error.URLError as exc:
                raise RuntimeError(f"Gemini URLError: {exc.reason}") from exc

            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError(f"Gemini response has no candidates: {data}")

            candidate = candidates[0]
            finish_reason = candidate.get("finishReason", "")
            parts = candidate.get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts).strip()

            if not text:
                raise RuntimeError(f"Gemini response has empty text: {data}")

            combined_text = f"{combined_text}\n{text}".strip() if combined_text else text

            if finish_reason != "MAX_TOKENS":
                break

            current_prompt = (
                "Tiep tuc dung phan dang do, khong lap lai noi dung da viet. "
                "Hoan thanh cau tra loi mot cach day du va ngan gon.\n\n"
                f"Noi dung da tra loi:\n{combined_text}"
            )

        return combined_text

    @staticmethod
    def _build_finance_context(
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        if end_date is None:
            end_date = datetime.now().date()
        if start_date is None:
            start_date = end_date - timedelta(days=90)

        tx_qs = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date,
        )

        income = tx_qs.filter(category__type="income").aggregate(total=Sum("amount"))["total"] or Decimal("0")
        expense = tx_qs.filter(category__type="expense").aggregate(total=Sum("amount"))["total"] or Decimal("0")
        by_category = list(
            tx_qs.filter(category__type="expense")
            .values("category__name")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")[:8]
        )
        recent_expenses = list(
            tx_qs.filter(category__type="expense")
            .select_related("category")
            .order_by("-transaction_date", "-id")[:15]
        )

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": float(income),
            "total_expense": float(expense),
            "balance": float(income - expense),
            "expense_by_category": [
                {
                    "category": item["category__name"] or "Khac",
                    "total": float(item["total"] or 0),
                    "count": item["count"],
                }
                for item in by_category
            ],
            "recent_expenses": [
                {
                    "date": t.transaction_date.isoformat(),
                    "amount": float(t.amount),
                    "category": t.category.name if t.category else "Khac",
                    "description": t.description or "",
                }
                for t in recent_expenses
            ],
        }

    @staticmethod
    def get_chat_response(user: User, message: str) -> str:
        finance_context = GeminiService._build_finance_context(user)
        system_prompt = (
            "Ban la tro ly tai chinh ca nhan bang tieng Viet. "
            "Tra loi ngan gon, de hieu, dua tren du lieu tai chinh duoc cung cap. "
            "Khong tu tao du lieu khong co trong context."
        )
        user_prompt = (
            f"Cau hoi nguoi dung: {message}\n\n"
            f"Du lieu tai chinh (JSON):\n{json.dumps(finance_context, ensure_ascii=True)}\n\n"
            "Hay tra loi bang tieng Viet, co so lieu cu the neu co."
        )
        return GeminiService._call_generate_content(system_prompt, user_prompt)

    @staticmethod
    def predict_next_month_spending_with_ai(
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        finance_context = GeminiService._build_finance_context(user, start_date=start_date, end_date=end_date)
        system_prompt = (
            "Ban la chuyen gia du bao chi tieu ca nhan. "
            "Phan tich data va tra ve dung JSON khong giai thich them."
        )
        user_prompt = (
            "Du lieu tai chinh (JSON):\n"
            f"{json.dumps(finance_context, ensure_ascii=True)}\n\n"
            "Tra ve JSON theo dung schema:\n"
            "{"
            '"predicted_amount": number, '
            '"confidence": "low|medium|high", '
            '"based_on_months": number, '
            '"reasoning": "string ngan"'
            "}"
        )

        raw = GeminiService._call_generate_content(system_prompt, user_prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)

        return {
            "predicted_amount": round(float(parsed.get("predicted_amount", 0)), 2),
            "confidence": parsed.get("confidence", "medium"),
            "based_on_months": int(parsed.get("based_on_months", 3)),
            "reasoning": parsed.get("reasoning", ""),
            "model": getattr(settings, "GEMINI_MODEL", GeminiService.DEFAULT_MODEL),
            "provider": "gemini",
        }
