"""Gemini Generative Language API (no Django)."""
import json
import urllib.error
import urllib.request
from typing import Any, Dict

from .config import settings


def _call_generate_content(system_prompt: str, user_prompt: str) -> str:
    api_key = (settings.gemini_api_key or "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    model = settings.gemini_model
    api_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    )
    timeout_seconds = settings.gemini_timeout_seconds
    max_output_tokens = settings.gemini_max_output_tokens

    combined_text = ""
    current_prompt = user_prompt
    max_continuation = 1

    for _ in range(max_continuation + 1):
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": current_prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": max_output_tokens,
            },
        }
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
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


def get_chat_response(finance_context: Dict[str, Any], message: str) -> str:
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
    return _call_generate_content(system_prompt, user_prompt)


def predict_next_month_spending_with_ai(finance_context: Dict[str, Any]) -> Dict[str, Any]:
    system_prompt = (
        "Ban la chuyen gia du bao chi tieu ca nhan. "
        "Phan tich data va tra ve dung JSON khong giai thich them."
    )
    user_prompt = (
        "Du lieu tai chinh (JSON):\n"
        f"{json.dumps(finance_context, ensure_ascii=True)}\n\n"
        "Tra ve JSON theo dung schema:\n"
        '{"predicted_amount": number, "confidence": "low|medium|high", '
        '"based_on_months": number, "reasoning": "string ngan"}'
    )
    raw = _call_generate_content(system_prompt, user_prompt)
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(cleaned)
    return {
        "predicted_amount": round(float(parsed.get("predicted_amount", 0)), 2),
        "confidence": parsed.get("confidence", "medium"),
        "based_on_months": int(parsed.get("based_on_months", 3)),
        "reasoning": parsed.get("reasoning", ""),
        "model": settings.gemini_model,
        "provider": "gemini",
    }
