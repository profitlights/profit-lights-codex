from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, bool]:
    return {"ok": True}


def _coerce_number(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _extract_number(payload: Any, key: str) -> Optional[float]:
    if not isinstance(payload, dict):
        return None
    for container in (payload, payload.get("metrics"), payload.get("financials")):
        if isinstance(container, dict) and key in container:
            return _coerce_number(container.get(key))
    return None


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))


def _score_band(score: int) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "amber"
    return "red"


def _build_needs_more_info(revenue: Optional[float], cogs: Optional[float], labor: Optional[float]) -> Dict[str, Any]:
    if revenue is None:
        missing_fields = ["revenue"]
        coach_prompt = (
            "Estimated. You’re not doing anything wrong. I need one anchor number so I don’t guess wrong. "
            "Could you share revenue for this period? A rough estimate or range is totally fine."
        )
        quick_replies = [
            "Revenue is $____",
            "Revenue range: $____–$____",
            "Not sure yet",
        ]
    else:
        missing_fields = ["cogs", "labor"]
        coach_prompt = (
            "Estimated. You’re not doing anything wrong. I need one anchor number so I don’t guess wrong. "
            "Could you share COGS or labor for this period? A rough estimate or range is totally fine."
        )
        quick_replies = [
            "COGS is $____",
            "Labor is $____",
            "Either one is fine",
        ]

    return {
        "message_intent": "NEEDS_MORE_INFO",
        "missing_fields": missing_fields,
        "coach_prompt": coach_prompt,
        "quick_replies": quick_replies,
        "score": {"estimated": True},
        "insight": {},
        "action_step": {},
    }


def _build_insight_action(
    revenue: Optional[float],
    cogs: Optional[float],
    labor: Optional[float],
) -> Dict[str, Any]:
    score = 75
    cogs_ratio = None
    labor_ratio = None

    if revenue:
        if cogs is not None:
            cogs_ratio = cogs / revenue
        if labor is not None:
            labor_ratio = labor / revenue

    if cogs_ratio is not None and cogs_ratio > 0.40:
        score -= 15
    if labor_ratio is not None and labor_ratio > 0.35:
        score -= 15

    score = _clamp_score(score)
    band = _score_band(score)

    if cogs_ratio is not None and cogs_ratio > 0.40:
        insight_text = "Food costs are running high compared to revenue."
        action_title = "Trim food costs fast"
        action_bullets = [
            "Review your top 5 items and flag any with rising ingredient costs (15 minutes).",
            "Pick one item to reprice or portion-adjust today (10 minutes).",
        ]
    elif labor_ratio is not None and labor_ratio > 0.35:
        insight_text = "Labor is running high compared to revenue."
        action_title = "Smooth the next shift"
        action_bullets = [
            "Compare last week’s sales by hour and trim one low-traffic slot (15 minutes).",
            "Check tomorrow’s schedule for one quick swap or cut (10 minutes).",
        ]
    else:
        insight_text = "You’re in a steady spot overall."
        action_title = "Keep the steady rhythm"
        action_bullets = [
            "Pick one top-selling item and confirm pricing versus costs (10 minutes).",
            "Spot-check yesterday’s labor versus sales for one small tweak (15 minutes).",
        ]

    estimated = not (revenue is not None and (cogs is not None or labor is not None))

    return {
        "message_intent": "INSIGHT_ACTION",
        "missing_fields": [],
        "coach_prompt": "Here’s what stands out — and the one thing to focus on next.",
        "score": {
            "value": score,
            "band": band,
            "estimated": estimated,
        },
        "insight": {"text": insight_text},
        "action_step": {
            "title": action_title,
            "bullets": action_bullets,
        },
    }


@app.post("/analyze_upload")
async def analyze_upload(request: Request) -> Dict[str, Any]:
    try:
        payload = await request.json()
    except ValueError:
        payload = {}

    revenue = _extract_number(payload, "revenue")
    cogs = _extract_number(payload, "cogs")
    labor = _extract_number(payload, "labor")

    if revenue is None or (cogs is None and labor is None):
        return _build_needs_more_info(revenue, cogs, labor)

    return _build_insight_action(revenue, cogs, labor)
