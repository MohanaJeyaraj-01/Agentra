from enum import Enum


class State(Enum):
    QUIZ = "quiz"
    DIAGNOSE = "diagnose"
    TEACH = "teach"
    RE_QUIZ = "re_quiz"
    EVALUATE = "evaluate"
    NEXT_QUESTION = "next_question"
    MENTOR = "mentor"
    FINISHED = "finished"


VALID_MISCONCEPTIONS = {"M1", "M2", "M3"}


class TutorFlow:
    def __init__(self):
        self.state = State.QUIZ
        self.misconception = None

        # Number of failed re-quizzes in the current remediation cycle.
        self.remediation_attempts = 0
        self.max_remediation_attempts = 2

        self.used_strategies = []
        self.retry_original_question = False

        self.model_calls = 0
        self.max_model_calls = 20

    def count_model_call(self):
        if self.model_calls >= self.max_model_calls:
            self.state = State.MENTOR
            raise RuntimeError("Maximum model-call limit reached.")

        self.model_calls += 1

    def move(self, event=None):
        if self.state == State.QUIZ:
            self.state = State.DIAGNOSE

        elif self.state == State.DIAGNOSE:
            if event == "correct":
                self.state = State.NEXT_QUESTION

            elif event in VALID_MISCONCEPTIONS:
                self.misconception = event
                self.remediation_attempts = 0
                self.used_strategies = []
                self.state = State.TEACH

            else:
                self.misconception = None
                self.retry_original_question = True
                self.state = State.MENTOR

        elif self.state == State.TEACH:
            self.state = State.RE_QUIZ

        elif self.state == State.RE_QUIZ:
            self.state = State.EVALUATE

        elif self.state == State.EVALUATE:
            if event == "pass":
                self.state = State.NEXT_QUESTION

            elif event == "fail":
                self.remediation_attempts += 1

                if self.remediation_attempts >= self.max_remediation_attempts:
                    self.state = State.MENTOR
                else:
                    self.state = State.TEACH

            elif event == "mentor_required":
                self.state = State.MENTOR

            else:
                self.state = State.MENTOR

        elif self.state == State.MENTOR:
            if event == "resolve":
                self.state = State.FINISHED

            elif event == "continue":
                if self.misconception in VALID_MISCONCEPTIONS:
                    self.remediation_attempts = 0
                    self.used_strategies = []
                    self.state = State.TEACH
                else:
                    self.retry_original_question = True
                    self.state = State.QUIZ

            elif event == "retry":
                self.retry_original_question = True
                self.state = State.QUIZ

            else:
                self.state = State.FINISHED

        elif self.state == State.NEXT_QUESTION:
            self.state = State.FINISHED