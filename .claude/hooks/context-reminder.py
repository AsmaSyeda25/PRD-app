#!/usr/bin/env python3
"""Stop hook: nudge to run /checkpoint as context usage climbs.

Estimates current context usage from the most recent assistant turn's token
usage in the transcript (input + cache-read + cache-creation tokens ≈ the
context sent to the model), and emits a one-time systemMessage as usage crosses
60% / 75% / 90%. Debounced via a per-session state file so it never spams.

Context window defaults to 200000 tokens; override with CLAUDE_CTX_WINDOW.
"""
import json
import os
import sys

THRESHOLDS = [60, 75, 90]
RESET_BELOW = 55  # if usage drops below this (e.g. after a compaction), re-arm


def read_stdin_json():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def latest_context_tokens(transcript_path):
    """Return the input-side token count of the most recent assistant turn."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    used = None
    try:
        with open(transcript_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                usage = (obj.get("message") or {}).get("usage") or {}
                if "input_tokens" in usage:
                    used = (
                        usage.get("input_tokens", 0)
                        + usage.get("cache_read_input_tokens", 0)
                        + usage.get("cache_creation_input_tokens", 0)
                    )
    except Exception:
        return None
    return used


def load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return int(json.load(fh).get("reminded", 0))
    except Exception:
        return 0


def save_state(path, level):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"reminded": level}, fh)
    except Exception:
        pass


def main():
    data = read_stdin_json()
    transcript = data.get("transcript_path", "")
    window = int(os.environ.get("CLAUDE_CTX_WINDOW", "200000") or "200000")

    used = latest_context_tokens(transcript)
    if not used or window <= 0:
        return  # nothing to report

    pct = used / window * 100.0

    state_path = (transcript + ".ctxreminder") if transcript else ""
    reminded = load_state(state_path) if state_path else 0

    # Re-arm after a compaction shrinks the context back down.
    if pct < RESET_BELOW and reminded != 0:
        save_state(state_path, 0)
        reminded = 0

    # Highest threshold now crossed that we haven't reminded about yet.
    crossed = [t for t in THRESHOLDS if pct >= t and t > reminded]
    if not crossed:
        return

    level = max(crossed)
    save_state(state_path, level)

    used_k = round(used / 1000)
    win_k = round(window / 1000)
    if level >= 90:
        msg = (f"🚨 Context ~{pct:.0f}% used ({used_k}k/{win_k}k) — auto-compact is near. "
               f"Run /checkpoint now, then /compact, to stay in control.")
    elif level >= 75:
        msg = (f"⚠️ Context ~{pct:.0f}% used ({used_k}k/{win_k}k). "
               f"Good time to run /checkpoint, then /compact.")
    else:
        msg = (f"🔔 Context ~{pct:.0f}% used ({used_k}k/{win_k}k) — you asked to compact around 60%. "
               f"Run /checkpoint, then /compact.")

    print(json.dumps({"systemMessage": msg, "suppressOutput": True}))


if __name__ == "__main__":
    main()
