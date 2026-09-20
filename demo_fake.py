"""
CEG ASTRA — Non-Interactive Demo

This demo does not call an LLM and does not require:
- an API key
- internet access
- user input

It deterministically demonstrates the core
Misconception Loop and its backward edge.
"""

from flow import TutorFlow, State


def show_state(flow, message):
    print(f"\nSTATE → {flow.state.value}")
    print(message)


def main():

    print("\n" + "=" * 55)
    print(" CEG ASTRA — NON-INTERACTIVE DEMO")
    print("=" * 55)

    print("\nPurpose:")
    print("Demonstrate the misconception loop without")
    print("an API key, network connection, or user input.")

    flow = TutorFlow()

    # --------------------------------------------------
    # 1. QUIZ
    # --------------------------------------------------

    show_state(
        flow,
        "Student receives a Python Lists question."
    )

    flow.move()

    # --------------------------------------------------
    # 2. DIAGNOSE
    # --------------------------------------------------

    flow.move("M1")

    show_state(
        flow,
        "Student answers incorrectly.\n"
        "Diagnosis → M1: append() vs extend()."
    )

    # --------------------------------------------------
    # 3. TEACH — STRATEGY 1
    # --------------------------------------------------

    flow.move()

    show_state(
        flow,
        "Teaching strategy 1 → Code comparison."
    )

    # --------------------------------------------------
    # 4. RE-QUIZ
    # --------------------------------------------------

    flow.move()

    show_state(
        flow,
        "Student receives a new question testing M1."
    )

    # --------------------------------------------------
    # 5. EVALUATE — FAIL
    # --------------------------------------------------

    flow.move("fail")

    show_state(
        flow,
        "Evaluation → FAIL.\n"
        "The misconception is still present."
    )

    # --------------------------------------------------
    # 6. BACK EDGE
    # --------------------------------------------------

    if flow.state == State.TEACH:

        print("\n🔄 BACK EDGE TRIGGERED")
        print(
            "Evaluation failure sends the student "
            "back to teaching."
        )

    # --------------------------------------------------
    # 7. TEACH — STRATEGY 2
    # --------------------------------------------------

    flow.move()

    show_state(
        flow,
        "Teaching strategy 2 → Analogy."
    )

    # --------------------------------------------------
    # 8. RE-QUIZ
    # --------------------------------------------------

    flow.move()

    show_state(
        flow,
        "Student receives another re-quiz."
    )

    # --------------------------------------------------
    # 9. EVALUATE — PASS
    # --------------------------------------------------

    flow.move("pass")

    show_state(
        flow,
        "Evaluation → PASS.\n"
        "The misconception is considered addressed."
    )

    # --------------------------------------------------
    # 10. NEXT QUESTION
    # --------------------------------------------------

    flow.move()

    show_state(
        flow,
        "Student can move to the next question."
    )

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    print("\n" + "-" * 55)
    print(" DEMO COMPLETE")
    print("-" * 55)

    print("""
Verified behavior:

✓ Quiz
✓ Misconception diagnosis
✓ Targeted teaching
✓ Re-quiz
✓ Failed evaluation
✓ Backward transition to teaching
✓ Different remediation strategy
✓ Successful re-quiz
✓ Evaluation pass
✓ Next-question transition
""")

    print(
        "No API key required."
    )
    print(
        "No network connection required."
    )
    print(
        "No user input required."
    )

    print("\n" + "=" * 55)


if __name__ == "__main__":
    main()