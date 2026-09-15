import json
from pathlib import Path

from flow import TutorFlow, State
from agents import diagnose, teach, evaluate
from store import load_state, save_state, record, update_misconception


QUESTIONS = json.loads(
    Path("questions.json").read_text(encoding="utf-8")
)

MISCONCEPTIONS = json.loads(
    Path("misconceptions.json").read_text(encoding="utf-8")
)

VALID_MISCONCEPTIONS = {"M1", "M2", "M3"}


def get_question(question_id):
    return next(q for q in QUESTIONS if q["id"] == question_id)


def choose_requiz(original, misconception, used_ids):
    """Select a different question that tests the same misconception."""

    priority = {
        "M1": ["Q4", "Q3", "Q1"],
        "M2": ["Q7", "Q6", "Q8"],
        "M3": ["Q10", "Q11", "Q12"],
    }

    for question_id in priority.get(misconception, []):
        if question_id not in used_ids:
            return get_question(question_id)

    candidates = [
        q for q in QUESTIONS
        if q["misconception"] == misconception
        and q["id"] not in used_ids
    ]

    return candidates[0] if candidates else None


def ask_student(question):
    print("\nQUESTION")
    print(question["question"])
    return input("\nYour answer: ").strip()


def ask_for_nonblank_answer(question):
    """Keep asking until the student enters a nonblank answer."""

    while True:
        answer = ask_student(question)

        if answer:
            return answer

        print("Please enter an answer. A blank response can't be diagnosed.")


def mentor_review(state, misconception):
    print("\n👨‍🏫 MENTOR REVIEW REQUIRED")
    print(f"Student: {state['student_id']}")
    print(f"Misconception: {misconception}")
    print("The autonomous tutor has stopped after its allowed attempts.")

    can_continue = misconception in VALID_MISCONCEPTIONS

    print("Choices:")
    print("  resolve  - mark the misconception resolved and finish")

    if can_continue:
        print("  continue - allow another teaching/re-quiz cycle")

    print("  retry    - ask the original question again")

    allowed = {"resolve", "retry"}

    if can_continue:
        allowed.add("continue")

    while True:
        decision = input(
            "Mentor decision (resolve / continue / retry): "
        ).strip().lower()

        if decision in allowed:
            break

        if can_continue:
            print("Please enter resolve, continue, or retry.")
        else:
            print(
                "No valid misconception was identified. "
                "Please enter resolve or retry."
            )

    record(state, "mentor_answer", {"decision": decision})
    save_state(state["student_id"], state)

    return decision


def run(student_id="student_001", first_question_id="Q2"):
    state = load_state(student_id)
    flow = TutorFlow()

    original_question = get_question(first_question_id)
    question = original_question

    used_ids = {question["id"]}
    student_answer = None

    print("\n========================================")
    print(" CEG ASTRA — MISCONCEPTION LOOP")
    print("========================================")
    print(f"Student: {student_id}")

    while flow.state != State.FINISHED:

        # QUIZ
        if flow.state == State.QUIZ:
            print(f"\nSTATE → {flow.state.value}")

            if flow.retry_original_question:
                question = original_question
                flow.retry_original_question = False
                phase = "mentor_retry"
            else:
                phase = "initial"

            student_answer = ask_for_nonblank_answer(question)

            record(state, "answer", {
                "question_id": question["id"],
                "answer": student_answer,
                "phase": phase,
            })
            save_state(student_id, state)

            flow.move()

        # DIAGNOSE
        elif flow.state == State.DIAGNOSE:
            print(f"\nSTATE → {flow.state.value}")

            flow.count_model_call()

            result = diagnose(
                question["question"],
                question["correct_answer"],
                student_answer,
            )

            record(state, "diagnosis", result)
            save_state(student_id, state)

            print("Diagnosis:", json.dumps(result, indent=2))

            if result.get("is_correct"):
                flow.move("correct")
            else:
                misconception = result.get("misconception")

                if misconception not in VALID_MISCONCEPTIONS:
                    flow.move("unknown")
                else:
                    flow.move(misconception)

        # TEACH
        elif flow.state == State.TEACH:
            print(f"\nSTATE → {flow.state.value}")
            print(f"Misconception: {flow.misconception}")
            print(
                "Remediation attempt:",
                flow.remediation_attempts + 1,
            )

            # Defensive guard: never call teach() with an invalid ID.
            if flow.misconception not in VALID_MISCONCEPTIONS:
                print(
                    "No valid misconception is available to teach. "
                    "Returning to the original question."
                )
                flow.retry_original_question = True
                flow.state = State.QUIZ
                continue

            previous = state["misconceptions"].get(
                flow.misconception,
                {},
            ).get("strategies_used", [])

            # Combine saved history with strategies used during this run.
            strategies_used = list(dict.fromkeys(
                previous + flow.used_strategies
            ))

            flow.count_model_call()

            lesson = teach(
                flow.misconception,
                strategies_used,
                flow.remediation_attempts + 1,
            )

            strategy = lesson.get("strategy")

            if strategy:
                flow.used_strategies.append(strategy)

            update_misconception(
                state,
                flow.misconception,
                status="unresolved",
                attempts=flow.remediation_attempts + 1,
                strategy=strategy,
            )

            record(state, "teaching", lesson)
            save_state(student_id, state)

            print(f"Strategy: {strategy}")
            print(f"\n{lesson.get('explanation', '')}")

            if lesson.get("example"):
                print("\nExample:")
                print(lesson["example"])

            flow.move()

        # RE-QUIZ
        elif flow.state == State.RE_QUIZ:
            print(f"\nSTATE → {flow.state.value}")

            requiz = choose_requiz(
                original_question,
                flow.misconception,
                used_ids,
            )

            if requiz is None:
                print("No unused re-quiz question remains.")
                flow.state = State.MENTOR
                continue

            question = requiz
            used_ids.add(question["id"])
            student_answer = ask_for_nonblank_answer(question)

            record(state, "answer", {
                "question_id": question["id"],
                "answer": student_answer,
                "phase": "requiz",
                "attempt": flow.remediation_attempts,
            })
            save_state(student_id, state)

            flow.move()

        # EVALUATE
        elif flow.state == State.EVALUATE:
            print(f"\nSTATE → {flow.state.value}")

            flow.count_model_call()

            result = evaluate(
                flow.misconception,
                question["question"],
                question["correct_answer"],
                student_answer,
                flow.remediation_attempts,
            )

            record(state, "evaluation", result)
            save_state(student_id, state)

            print("Evaluation:", json.dumps(result, indent=2))

            if result.get("result") == "pass":
                update_misconception(
                    state,
                    flow.misconception,
                    status="resolved",
                    attempts=flow.remediation_attempts,
                )
                save_state(student_id, state)
                flow.move("pass")

            elif result.get("result") == "fail":
                flow.move("fail")

            else:
                flow.move(result.get("result"))

        # NEXT QUESTION
        elif flow.state == State.NEXT_QUESTION:
            print(f"\nSTATE → {flow.state.value}")

            if flow.misconception:
                update_misconception(
                    state,
                    flow.misconception,
                    status="resolved",
                    attempts=flow.remediation_attempts,
                )
                save_state(student_id, state)

            print("Misconception resolved.")
            print("Student can continue to the next question.")
            flow.move()

        # MENTOR REVIEW
        elif flow.state == State.MENTOR:
            print(f"\nSTATE → {flow.state.value}")

            decision = mentor_review(state, flow.misconception)

            if decision == "resolve" and flow.misconception:
                update_misconception(
                    state,
                    flow.misconception,
                    status="resolved",
                    attempts=flow.remediation_attempts,
                )
                save_state(student_id, state)

            if (
                decision == "continue"
                and flow.misconception not in VALID_MISCONCEPTIONS
            ):
                print(
                    "Cannot continue teaching without a valid misconception. "
                    "Retrying the original question."
                )
                flow.move("retry")

            else:
                if decision == "continue":
                    # Start a fresh re-quiz pool for the new mentor-approved cycle.
                    # Keep the original question excluded.
                    used_ids = {original_question["id"]}

                flow.move(decision)

    print("\nSTATE → finished")
    print("========================================")
    print("Run finished.")
    print("Student state saved to student_state.json")
    print("========================================")


if __name__ == "__main__":
    student = input("Student ID [student_001]: ").strip() or "student_001"
    run(student_id=student, first_question_id="Q9")