from __future__ import annotations

import json
from typing import Any, Dict

import httpx

from ..config import settings


class AISummaryError(RuntimeError):
    """Raised when the AI summary process fails."""


def _build_ai_payload(analysis: Dict[str, Any]) -> Dict[str, Any]:
    vehicles = analysis.get("vehicles", [])
    economy = analysis.get("economy_extremes", {})
    savers = economy.get("top_savers", [])
    risks = economy.get("top_risks", [])

    condensed = {
        "overview": {
            "energy_limit_kwh": analysis.get("energy_limit_kwh"),
            "period_months": analysis.get("period_months"),
            "total_vehicles": analysis.get("total_vehicles"),
            "total_tours": analysis.get("total_tours"),
            "total_mileage": analysis.get("total_mileage"),
        },
        "feasibility_breakdown": analysis.get("feasibility_breakdown", {}),
        "cost_efficiency_breakdown": analysis.get("cost_efficiency_breakdown", {}),
        "both_yes_count": analysis.get("both_yes_count"),
        "fuel_summary": analysis.get("fuel_summary", []),
        "top_savers": savers[:3],
        "top_risks": risks[:3],
        "daily_trend": analysis.get("daily_trend", [])[-7:],
    }
    # include aggregate stats if available
    if vehicles:
        condensed["sample"] = vehicles[:5]
    return condensed


def _compose_prompt(data: Dict[str, Any]) -> str:
    instruction = (
        "You are a fleet electrification consultant. Analyse the provided KPI JSON and produce a concise interpretation. "
        "Focus on BEV feasibility, cost efficiency, and operational risks. Return valid JSON with the schema: "
        "{\"headline\": string, \"bullets\": string[3], \"cautions\": string[<=3]}. Do not include markdown."
    )
    payload = json.dumps(data, ensure_ascii=False)
    return f"{instruction}\n\nDATA:\n{payload}"


async def generate_ai_summary(analysis: Dict[str, Any]) -> Dict[str, Any]:
    if not settings.google_api_key:
        raise AISummaryError("AI summary disabled: missing GOOGLE_API_KEY")

    prompt = _compose_prompt(_build_ai_payload(analysis))

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 512,
        },
    }

    model = settings.google_model
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent"
    params = {"key": settings.google_api_key}

    async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
        response = await client.post(endpoint, params=params, json=body)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:  # pragma: no cover - depends on external service
            raise AISummaryError(f"AI service error: {exc.response.status_code}") from exc

    payload = response.json()
    candidates = payload.get("candidates") or []
    if not candidates:
        raise AISummaryError("AI service returned no candidates")

    text_parts = []
    for candidate in candidates:
        content = candidate.get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            txt = part.get("text")
            if txt:
                text_parts.append(txt)
    if not text_parts:
        raise AISummaryError("AI response missing text body")

    combined = "\n".join(text_parts).strip()

    try:
        parsed = json.loads(combined)
    except json.JSONDecodeError as exc:
        raise AISummaryError("AI response was not valid JSON") from exc

    headline = parsed.get("headline")
    bullets = parsed.get("bullets")
    cautions = parsed.get("cautions")
    if not isinstance(headline, str) or not isinstance(bullets, list):
        raise AISummaryError("AI response missing expected keys")

    return {
        "headline": headline,
        "bullets": [str(item) for item in bullets[:5]],
        "cautions": [str(item) for item in (cautions or [])[:5]],
        "raw": combined,
    }

