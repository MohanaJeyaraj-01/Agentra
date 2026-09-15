import json
from pathlib import Path
from datetime import datetime, timezone

STATE_FILE = Path("student_state.json")


def _now():
    return datetime.now(timezone.utc).isoformat()


def load_state(student_id):
    if not STATE_FILE.exists():
        return new_state(student_id)

    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return data.get(student_id, new_state(student_id))


def save_state(student_id, state):
    all_states = {}
    if STATE_FILE.exists():
        all_states = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    state["updated_at"] = _now()
    all_states[student_id] = state
    STATE_FILE.write_text(json.dumps(all_states, indent=2), encoding="utf-8")


def new_state(student_id):
    return {
        "student_id": student_id,
        "misconceptions": {},
        "history": [],
        "updated_at": _now()
    }


def record(state, kind, data):
    state["history"].append({
        "timestamp": _now(),
        "kind": kind,
        "data": data
    })


def update_misconception(state, misconception_id, status=None, attempts=None, strategy=None):
    item = state["misconceptions"].setdefault(
        misconception_id,
        {"status": "unresolved", "attempts": 0, "strategies_used": []}
    )

    if status is not None:
        item["status"] = status
    if attempts is not None:
        item["attempts"] = attempts
    if strategy is not None and strategy not in item["strategies_used"]:
        item["strategies_used"].append(strategy)
