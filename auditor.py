import json
import os
import uuid
from datetime import datetime, timezone

from config import LOG_FILE, LLM_MODEL, VALID_TIERS

try:
    from safety import CLASSIFIER_PROMPT_VERSION
except Exception:  # keep the logger usable even if safety.py fails to import
    CLASSIFIER_PROMPT_VERSION = "unknown"

QUESTION_MAX_CHARS = 300
RESPONSE_PREVIEW_CHARS = 200
CONSOLE_QUESTION_CHARS = 60


def _truncate(text: str, limit: int) -> str:
    text = text or ""
    return text if len(text) <= limit else text[:limit]


def log_interaction(question: str, tier: str, response: str, reason: str = "") -> None:
    """
    Append a structured record of this interaction to the audit log (LOG_FILE, JSONL).

    Design is documented in specs/auditor-spec.md. One JSON object per line, written with
    json.dumps (never indent=) plus "\\n", in append mode. Creates logs/ if missing.

    `reason` is optional (default "") so the original 3-argument call still works;
    app.py passes the classifier's reason so each record says WHY the tier was chosen.

    Prints a one-line summary:
      [LOGGED] tier=caution | "How do I replace a bathroom faucet?" → 1243 chars
    """
    question = question or ""
    response = response or ""

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "interaction_id": uuid.uuid4().hex[:12],
        "tier": tier,
        "tier_valid": tier in VALID_TIERS,
        "classifier_reason": _truncate(reason, QUESTION_MAX_CHARS),
        "question": _truncate(question, QUESTION_MAX_CHARS),
        "question_chars": len(question),
        "response_preview": _truncate(response, RESPONSE_PREVIEW_CHARS),
        "response_chars": len(response),
        "model": LLM_MODEL,
        "classifier_prompt_version": CLASSIFIER_PROMPT_VERSION,
    }

    try:
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        # Never crash the user's request because logging failed, but make it loud.
        print(f"[AUDIT ERROR] Could not write to {LOG_FILE}: {e!r} | record={json.dumps(record)}")
        return

    short_q = question if len(question) <= CONSOLE_QUESTION_CHARS else question[:CONSOLE_QUESTION_CHARS - 1] + "…"
    print(f'[LOGGED] tier={tier} | "{short_q}" → {len(response)} chars')
