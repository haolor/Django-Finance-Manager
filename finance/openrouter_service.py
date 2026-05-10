"""
OpenRouter service for AI chat responses and predictions.
"""
import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Optional, List

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Sum

from .models import Transaction


class OpenrouterService:
    """Service call AI model via OpenRouter API (OpenAI compatible)."""

    DEFAULT_MODEL = "gpt-oss-120b"
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_TIMEOUT_SECONDS = 60
    DEFAULT_MAX_OUTPUT_TOKENS = 2000

    @staticmethod
    def _get_api_key() -> str:
        return (getattr(settings, "OPENROUTER_API_KEY", "") or "").strip()

    @staticmethod
    def _get_model() -> str:
        return getattr(settings, "AI_MODEL", OpenrouterService.DEFAULT_MODEL)

    @staticmethod
    def _call_generate_content(system_prompt: str, user_prompt: str) -> str:
        api_key = OpenrouterService._get_api_key()
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")

        model = OpenrouterService._get_model()
        timeout_seconds = int(
            getattr(settings, "AI_TIMEOUT_SECONDS", OpenrouterService.DEFAULT_TIMEOUT_SECONDS)
        )
        max_output_tokens = int(
            getattr(settings, "AI_MAX_OUTPUT_TOKENS", OpenrouterService.DEFAULT_MAX_OUTPUT_TOKENS)
        )

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_output_tokens,
            "temperature": 0.3,
        }

        req = urllib.request.Request(
            OpenrouterService.API_URL,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/haolor/Django-Finance-Manager", # Site URL for OpenRouter rankings
                "X-Title": "Django Finance Manager", # Site Title for OpenRouter rankings
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"AI API HTTPError {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"AI API URLError: {exc.reason}") from exc

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"AI response has no choices: {data}")

        text = choices[0].get("message", {}).get("content", "").strip()

        if not text:
            raise RuntimeError(f"AI response has empty content: {data}")

        return text

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
        finance_context = OpenrouterService._build_finance_context(user)
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
        return OpenrouterService._call_generate_content(system_prompt, user_prompt)

    @staticmethod
    def predict_next_month_spending_with_ai(
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        finance_context = OpenrouterService._build_finance_context(user, start_date=start_date, end_date=end_date)
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

        raw = OpenrouterService._call_generate_content(system_prompt, user_prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)

        return {
            "predicted_amount": round(float(parsed.get("predicted_amount", 0)), 2),
            "confidence": parsed.get("confidence", "medium"),
            "based_on_months": int(parsed.get("based_on_months", 3)),
            "reasoning": parsed.get("reasoning", ""),
            "model": OpenrouterService._get_model(),
            "provider": "openrouter",
        }
    @staticmethod
    def analyze_trends_with_ai(
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        finance_context = OpenrouterService._build_finance_context(user, start_date=start_date, end_date=end_date)
        # Lấy thêm dữ liệu theo tuần để AI phân tích tốt hơn
        tx_qs = Transaction.objects.filter(
            user=user,
            transaction_date__gte=finance_context["start_date"],
            transaction_date__lte=finance_context["end_date"],
        )
        
        system_prompt = (
            "Ban la chuyen gia phan tich xu huong tai chinh. "
            "Hay phan tich du lieu va tra ve JSON."
        )
        user_prompt = (
            f"Du lieu (JSON):\n{json.dumps(finance_context)}\n\n"
            "Hay tra ve JSON theo schema:\n"
            "{"
            '"trend": "increasing|decreasing|stable", '
            '"trend_percentage": number, '
            '"summary": "string ngan", '
            '"weekly_data": [{"week": "YYYY-MM-DD", "expense": number, "income": number, "balance": number}]'
            "}"
        )

        raw = OpenrouterService._call_generate_content(system_prompt, user_prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)
        
        parsed["model"] = OpenrouterService._get_model()
        parsed["provider"] = "openrouter"
        return parsed

    @staticmethod
    def detect_anomalies_with_ai(
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        finance_context = OpenrouterService._build_finance_context(user, start_date=start_date, end_date=end_date)
        system_prompt = (
            "Ban la chuyen gia phat hien bat thuong tai chinh. "
            "Dua tren du lieu chi tieu, hay tim cac giao dich bat thuong (chi tieu qua cao, tan suat la, v.v.). "
            "Tra ve JSON array."
        )
        user_prompt = (
            f"Du lieu chi tieu (JSON):\n{json.dumps(finance_context['recent_expenses'])}\n\n"
            "Tra ve JSON array cac doi tuong:\n"
            "{"
            '"id": number, '
            '"amount": number, '
            '"category": "string", '
            '"date": "YYYY-MM-DD", '
            '"description": "string", '
            '"deviation": number, '
            '"reason": "tai sao bat thuong"'
            "}"
        )

        raw = OpenrouterService._call_generate_content(system_prompt, user_prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)

    @staticmethod
    def suggest_savings_with_ai(
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        finance_context = OpenrouterService._build_finance_context(user, start_date=start_date, end_date=end_date)
        system_prompt = (
            "Ban la chuyen gia lap ke hoach tiet kiem. "
            "Hay dua ra cac goi y cu the de tiet kiem dua tren chi tieu. "
            "Tra ve JSON."
        )
        user_prompt = (
            f"Du lieu tai chinh (JSON):\n{json.dumps(finance_context)}\n\n"
            "Tra ve JSON theo schema:\n"
            "{"
            '"total_potential_savings": number, '
            '"monthly_expense": number, '
            '"savings_rate": number, '
            '"overall_recommendation": ["string"], '
            '"suggestions": ['
            '{"category": "string", "suggestion": "string", "potential_savings": number, "reasons": ["string"], "priority_score": number, "actionable_tips": ["string"]}'
            ']'
            "}"
        )

        raw = OpenrouterService._call_generate_content(system_prompt, user_prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)
        
        parsed["model"] = OpenrouterService._get_model()
        parsed["provider"] = "openrouter"
        return parsed
