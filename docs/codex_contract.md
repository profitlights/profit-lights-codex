# Profit Lights Codex Contract (MVP)

## Purpose
The Codex coaching engine analyzes an uploaded small-business data snapshot and returns a tiny, deterministic coaching response that answers:
"Am I okay — and what should I do next?"

## Job: analyze_upload

### Inputs
- A single upload payload that can be normalized into the `schemas/normalized.schema.json` shape.
- The system must attempt normalization from the raw `schemas/input.schema.json` shape.

### Outputs
The analyzer must return a JSON object that conforms to `schemas/output.schema.json` and includes:
- One score (0–100) and band (green / amber / red)
- One insight (short and calm)
- One action step (max 3 bullets, 5–30 minutes)

### Output intents
Use only:
- `INSIGHT_ACTION`
- `NEEDS_MORE_INFO`
- `UPLOAD_CONFIRMED`
- `ERROR_FRIENDLY`

### Missing data rule (gating)
Return value for all uploads **unless**:
- Revenue is missing, **or**
- BOTH COGS and Labor are missing

If gating data is missing:
- Set `message_intent = NEEDS_MORE_INFO`
- Provide a coachy prompt that reassures, explains why, and asks for only 1–2 items
- Mention that rough estimates are acceptable

### Determinism
- Keep responses short and consistent
- No dashboards, scenarios, or long reports
- One insight and one action only
