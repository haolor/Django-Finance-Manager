"""Aggregated finance data for the AI/NLP service (HTTP context endpoint)."""
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Optional

from django.contrib.auth.models import User
from django.db.models import Sum, Count

from .models import Transaction


def build_finance_context_for_ai(
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
