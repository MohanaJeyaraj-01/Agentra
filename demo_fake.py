from flow import TutorFlow, State


def main():
    flow = TutorFlow()

    print("QUIZ")
    flow.move()

    print("DIAGNOSE → M1")
    flow.move("M1")

    print("TEACH → strategy 1")
    flow.move()

    print("RE-QUIZ")
    flow.move()

    print("EVALUATE → FAIL")
    flow.move("fail")

    print("BACK EDGE → TEACH")
    flow.move()

    print("TEACH → strategy 2")
    flow.move()

    print("RE-QUIZ")
    flow.move()

    print("EVALUATE → PASS")
    flow.move("pass")

    print("NEXT QUESTION")
    flow.move()

    print("FINISHED")


if __name__ == "__main__":
    main()
