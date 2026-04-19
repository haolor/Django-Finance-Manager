"""HTTP client to Core Finance API (Django DRF)."""
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx

from .config import settings


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Token {token.strip()}"}


class CoreClient:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = (base_url or settings.core_api_base_url).rstrip("/")

    def get_finance_context(
        self,
        token: str,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        with httpx.Client(timeout=60.0) as client:
            r = client.get(
                f"{self.base_url}/api/ai/finance-context/",
                headers=_auth_headers(token),
                params=params,
            )
            r.raise_for_status()
            return r.json()

    def list_categories(self, token: str) -> List[Dict[str, Any]]:
        with httpx.Client(timeout=60.0) as client:
            r = client.get(f"{self.base_url}/api/categories/", headers=_auth_headers(token))
            r.raise_for_status()
            return r.json()

    def create_category(self, token: str, name: str, category_type: str) -> Dict[str, Any]:
        body = {
            "name": name,
            "description": "",
            "icon": "💰",
            "color": "#3B82F6",
            "type": category_type,
        }
        with httpx.Client(timeout=60.0) as client:
            r = client.post(
                f"{self.base_url}/api/categories/",
                headers={**_auth_headers(token), "Content-Type": "application/json"},
                json=body,
            )
            if r.status_code == 400:
                for c in self.list_categories(token):
                    if c.get("name") == name:
                        return c
            r.raise_for_status()
            return r.json()

    def ensure_category_id(self, token: str, name: str, category_type: str) -> int:
        for c in self.list_categories(token):
            if c.get("name") == name:
                return int(c["id"])
        created = self.create_category(token, name, category_type)
        return int(created["id"])

    def create_transaction(
        self,
        token: str,
        *,
        category_id: Optional[int],
        amount: Decimal,
        description: str,
        transaction_date,
        original_nlp_input: str,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "amount": str(amount),
            "description": description,
            "transaction_date": transaction_date.isoformat(),
            "original_nlp_input": original_nlp_input,
        }
        if category_id is not None:
            body["category"] = category_id
        with httpx.Client(timeout=60.0) as client:
            r = client.post(
                f"{self.base_url}/api/transactions/",
                headers={**_auth_headers(token), "Content-Type": "application/json"},
                json=body,
            )
            r.raise_for_status()
            return r.json()

    def get_local_predictions(
        self,
        token: str,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        with httpx.Client(timeout=60.0) as client:
            r = client.get(
                f"{self.base_url}/api/ai/predictions/",
                headers=_auth_headers(token),
                params=params,
            )
            r.raise_for_status()
            return r.json()
