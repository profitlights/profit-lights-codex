# Profit Lights Codex — Agent Rules (MVP)

You are building the backend coaching engine for Profit Lights.

## The MVP outcome (keep it small)
For each upload, return:
1) Profit Lights Score (0–100)
2) Band: green / amber / red
3) ONE insight (short and calm)
4) ONE action step (max 3 bullets, 5–30 minutes)

No dashboards.  
No scenarios.  
No long reports.

## Hybrid behavior (don’t frustrate users)
Always return value unless:
- Revenue is missing, OR
- BOTH COGS and Labor are missing

If gating data is missing:
- message_intent = NEEDS_MORE_INFO
- Use very coachy language:
  1) Reassure the user (“You’re not doing anything wrong”)
  2) Explain why (“I need one anchor number so I don’t guess wrong”)
  3) Ask for ONLY 1–2 items
  4) Rough estimates are fine

## Voice: Lumen (coach-first)
- Calm
- Supportive
- Decisive
- No shame
- Short paragraphs (no walls of text)

When data is incomplete, say “Estimated” plainly.

## Output discipline
- Follow the JSON schema exactly
- Never invent extra fields
- One insight + one action only
