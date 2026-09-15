from pathlib import Path
import json

from llm import call_llm, parse_json

PROMPT_DIR = Path("prompts")


def read_prompt(name):
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def diagnose(question, expected, student_answer):
    user = f"""
Question:
{question}

Expected answer:
{expected}

Student answer:
{student_answer}
"""

    raw = call_llm(read_prompt("diagnose.md"), user)
    return parse_json(raw)


STRATEGIES = {
    "M1": [
        "code_comparison",
        "analogy",
        "step_by_step_trace",
    ],
    "M2": [
        "position_analogy",
        "indexed_diagram",
        "code_trace",
    ],
    "M3": [
        "range_visualization",
        "index_diagram",
        "step_by_step_trace",
    ],
}


def choose_strategy(misconception, strategies_used):
    """
    Prefer a strategy not used before. If all strategies have been used,
    cycle back to the first strategy rather than crashing.
    """
    allowed = STRATEGIES.get(misconception, [])

    if not allowed:
        raise ValueError(f"Unknown misconception: {misconception}")

    for strategy in allowed:
        if strategy not in strategies_used:
            return strategy

    # All strategies have been used; cycle back to keep the tutor running.
    return allowed[len(strategies_used) % len(allowed)]


def teach(misconception, strategies_used, attempt):
    strategy = choose_strategy(misconception, strategies_used)

    user = f"""
Diagnosed misconception:
{misconception}

Teaching attempt:
{attempt}

Use this exact teaching strategy:
{strategy}

Strategies already used:
{json.dumps(strategies_used)}

Teach ONLY the diagnosed misconception.

Do not change the misconception.
Do not choose a different strategy.
Do not introduce unrelated Python concepts.

Return ONLY valid JSON.
"""

    raw = call_llm(read_prompt("teach.md"), user)
    lesson = parse_json(raw)

    # Python is the source of truth for workflow decisions.
    lesson["misconception"] = misconception
    lesson["strategy"] = strategy

    return lesson


def evaluate(
    misconception,
    question,
    expected,
    student_answer,
    attempt,
):
    user = f"""
Diagnosed misconception:
{misconception}

Re-quiz question:
{question}

Expected answer:
{expected}

Student answer:
{student_answer}

Remediation attempt:
{attempt}
"""

    raw = call_llm(read_prompt("evaluate.md"), user)
    return parse_json(raw)