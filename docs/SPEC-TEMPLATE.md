# CEG ASTRA — Agent-a-thon — Sep 2026

# AgentSpec — Misconception Loop

**Team:** Agentra  
**Department:** CSE  
**Submitted:** 15 September 2026

## 1. The setting

**Who exactly:** College students learning Python and practicing short programming questions.

**What they do today:** They solve quiz/code-output questions and, when wrong, usually see the correct answer or a generic explanation before moving on.

**Why that is hard:** A student can repeatedly make the same conceptual mistake—such as treating `append()` as if it flattened a list—without knowing what mental model caused the mistake.

## 2. The problem this solves

A student answers a Python list question incorrectly because they believe `append([3,4])` adds `3` and `4` separately. A normal quiz can mark the answer wrong and show the correct output, but it does not establish whether the student has understood the misconception. If the student fails another question for the same reason, the system should recognize the repeated misconception, try a different explanation, and stop for a mentor rather than repeating indefinitely.

## 3. What you are building

**Input:** A Python question, the student's answer, and the supported misconception set for the current slice.

**Output:** A diagnosis of the student's misconception, a targeted teaching attempt, a new re-quiz, and a final outcome of resolved, continued remediation, or mentor review.

**Never, however much a user wants it:** The system will not invent arbitrary misconceptions outside its supported set, expand into unrelated topics, or retry indefinitely.

**Why this is agentic, in your own words:** The system maintains student state across encounters, breaks the task into diagnosis/teaching/evaluation steps, changes strategy after failure, can send work backward from evaluation to teaching, and can stop in a mentor-review state.

## 4. A complete walkthrough

### Run: student `m1_robust_test`, misconception M1

**Step 1 — Quiz**

```text
What is the output?
a = [1, 2]
a.append([3, 4])
print(a)
```

Student answer:

```text
[1,2,3,4]
```

**Step 2 — Diagnose**

```json
{
  "is_correct": false,
  "misconception": "M1",
  "confidence": 0.95,
  "reason": "The student incorrectly flattened the appended list, indicating confusion between append (adds as a single element) and extend (adds elements individually)."
}
```

**Step 3 — Teach, attempt 1**

Strategy: `code_comparison`. The tutor explains that `append()` adds its argument as one element, while `extend()` adds the elements inside the argument separately.

**Step 4 — Re-quiz**

```text
What is the output?
a = ['A']
a.append(['B', 'C'])
print(a)
```

Student answer:

```text
['A','B','C']
```

**Step 5 — Evaluate**

```json
{
  "result": "fail",
  "reason": "Student flattened the nested list instead of appending it as a single element."
}
```

The evaluator sends the run backward to `TEACH`.

**Step 6 — Teach, attempt 2**

Strategy: `analogy`. The tutor uses a bag-and-box analogy to explain the difference between adding the whole list as one item and adding each item separately.

**Step 7 — Re-quiz**

```text
What is the output?
a = [1, 2]
a.extend([3, 4])
print(a)
```

Student answer:

```text
[1,2,[3,4]]
```

**Step 8 — Evaluate**

```json
{
  "result": "fail",
  "reason": "Incorrect output; shows misunderstanding of extend vs append."
}
```

The revision limit has been reached.

**Step 9 — Mentor**

The system enters mentor review for `m1_robust_test` and M1. The mentor chooses `resolve`, and the run finishes.

The key agentic transition is:

```text
EVALUATE (fail) → TEACH → RE-QUIZ → EVALUATE
```

## 5. Who is doing the thinking

| step | the agent does it | the human does it | what the human loses if the agent does it |
|---|---|---|---|
| Diagnose misconception | Analyze the student's answer and select a supported misconception | — | Human spends time identifying the error pattern manually |
| Choose teaching strategy | Select an unused strategy based on stored history | — | Human must remember previous explanations |
| Teach | Generate targeted explanation | — | Human teaching time |
| Evaluate re-quiz | Judge whether the answer still shows the misconception | — | Human repeatedly checks routine answers |
| Mentor review | — | Decide what to do after repeated failure | Human judgment is preserved |

**The question it asks, and who answers it:** The agent asks the mentor for `resolve`, `continue`, or `retry`. The mentor answers.

**What happens if nobody answers:** The current slice remains at mentor review rather than silently continuing autonomous remediation.

## 6. The state machine

```text
QUIZ
  ↓
DIAGNOSE
  ↓
TEACH
  ↓
RE_QUIZ
  ↓
EVALUATE ── pass ──→ NEXT_QUESTION
  │
  └── fail ─────────→ TEACH
                         │
                         └── after revision limit → MENTOR → FINISHED
```

| state | active / waiting / finished | what moves it on |
|---|---|---|
| QUIZ | active | Student submits an answer |
| DIAGNOSE | active | Diagnosis is produced |
| TEACH | active | Targeted remediation is produced |
| RE_QUIZ | active | Student submits re-quiz answer |
| EVALUATE | active | Pass moves forward; fail sends work backward |
| NEXT_QUESTION | active | Next question is selected |
| MENTOR | waiting | Mentor supplies a decision |
| FINISHED | finished | Nothing moves it again |

**What can send work backwards:** A failed `EVALUATE` sends the run back to `TEACH` so another remediation strategy can be attempted.

**What the run decides that the diagram cannot show:** Diagnosis identifies the misconception; teaching selects a strategy; evaluation determines pass/fail; stored strategy history influences the next strategy.

**Spend limit — what bounds cost:** Maximum 20 model calls per run.

**Revision limit — what bounds going backwards:** Maximum 2 autonomous remediation attempts for the same misconception before mentor review.

## 7. The data model

The system stores per-student JSON state in `student_state.json`.

Important stored information includes student ID, misconception history, strategies already used for each misconception, and run records such as answers, diagnoses, teaching attempts, evaluations, and mentor decisions.

| kind | written by | when |
|---|---|---|
| answer | quiz flow | Student submits an answer |
| diagnosis | diagnosis step | Misconception is identified |
| teaching | teaching step | Remediation is generated |
| evaluation | evaluation step | Re-quiz is judged |
| mentor_question | mentor step | Autonomous attempts are exhausted |
| mentor_answer | mentor step | Mentor supplies a decision |

## 8. Step-by-step contracts

### Diagnose · `DIAGNOSE` → `TEACH`
- **What:** Determine whether the answer is correct and, if incorrect, identify one supported misconception.
- **Why this way:** The core problem is identifying the reason for the error, not merely marking it wrong.
- **Reads / writes:** Reads question and student answer; writes diagnosis.
- **Done when:** A structured diagnosis is available.

### Teach · `TEACH` → `RE_QUIZ`
- **What:** Explain the diagnosed misconception using a teaching strategy.
- **Why this way:** Different explanations can be tried after failure.
- **Reads / writes:** Reads misconception and previous strategy history; writes teaching record.
- **Done when:** A targeted explanation is shown.

### Evaluate · `EVALUATE` → `NEXT_QUESTION` or `TEACH`/`MENTOR`
- **What:** Judge the re-quiz answer.
- **Why this way:** Evaluation determines whether remediation worked.
- **Reads / writes:** Reads question and answer; writes evaluation.
- **Done when:** The result is pass or fail and the flow can route accordingly.

### Mentor · `MENTOR` → `FINISHED` or continued flow
- **What:** Ask for human intervention after the autonomous revision limit.
- **Why this way:** The system must know when to stop rather than tutor forever.
- **Reads / writes:** Reads misconception and attempt history; writes mentor decision.
- **Done when:** A mentor decision is supplied.

## 9. The second encounter

The second encounter uses the same student's stored state instead of starting from an empty history.

For `m1_robust_test`:

**First encounter:**
- Attempt 1: `code_comparison`
- Attempt 2: `analogy`

**Second encounter:**
- Attempt 1: `step_by_step_trace`
- Attempt 2: `code_comparison`

The second run therefore does something a fresh conversation cannot: it reads previous strategy history and changes the strategy selected for the student. This proves persistence affects agent behavior rather than merely storing logs.

## 10. Files and responsibilities

| file | owns | done when |
|---|---|---|
| `main.py` | CLI entry point and question selection | A student can run a complete session |
| `flow.py` | State machine and limits | States transition correctly, including the backward edge |
| `agents.py` | Diagnosis, teaching, evaluation and strategy selection | Agent steps return usable decisions |
| `store.py` | Persistent student state | State survives between encounters |
| `llm.py` | OpenRouter model calls and JSON parsing | Model output is safely handled |
| `questions.json` | Question bank | Questions cover supported misconceptions |
| `misconceptions.json` | Supported misconception definitions | Diagnosis scope is explicit |
| `prompts/` | Model instructions | Diagnosis, teaching and evaluation have separate prompts |
| `demo_fake.py` | Fake/demo path | Flow can be exercised without a live model |

## 11. What this deliberately does not do

1. **No multiple-topic tutor.** The live slice focuses on Python Lists so the team can test the full loop instead of spreading effort across a curriculum.
2. **No knowledge graph or vector database.** The current problem does not require retrieval infrastructure; the explicit misconception/question set is enough for the two-day slice.
3. **No arbitrary model-invented misconceptions.** Diagnoses are restricted to the supported misconception set so the demo can be evaluated against known cases.
4. **No endless retries.** Two autonomous remediation attempts are the limit; repeated failure goes to a human mentor.
5. **No claim of permanent mastery.** Passing a re-quiz is not a scientific measurement of long-term mastery.

## 12. Build order

| phase | what lands | hours |
|---|---|---|
| 1 | Hard-coded end-to-end state machine and question flow | 2 |
| | **cut line:** complete fake run from quiz through evaluation | |
| 2 | Live model calls, structured diagnosis/teaching/evaluation, persistent JSON state | 3 |
| | **cut line:** one live misconception loop works end to end | |
| 3 | Backward evaluation-to-teaching loop, strategy limits, mentor state | 2 |
| | **cut line:** failed re-quiz causes a different remediation attempt | |
| 4 | Three misconceptions, second-encounter persistence test, demo cleanup | 2 |
| | **cut line:** live demo plus evidence that stored state changes later behavior | |

## 13. The demo

1. Start with a Python list question.
2. Enter a deliberately wrong answer.
3. Show diagnosis identifying M1.
4. Show the first targeted explanation.
5. Enter a wrong re-quiz answer.
6. Show `EVALUATE → TEACH`.
7. Show the different second strategy.
8. Fail again and show mentor escalation.
9. Run the same student again and show stored strategy history changing the first strategy.

**Which beat is the argument:** The failed re-quiz causing a backward transition and a different remediation strategy.

**What is live and what is recorded:** The live demo uses the running program and live model responses; the walkthrough values are recorded evidence from tested runs.

## 14. How this grows

The core state machine can support additional misconception/question records without changing the main loop. New questions can be added to `questions.json`, misconceptions to `misconceptions.json`, and teaching strategies to the strategy definitions in `agents.py`.

A larger deployment would eventually need stronger storage/concurrency handling than the current per-student JSON file.

## 15. What you are least sure about

1. **Diagnosis reliability:** Whether the model consistently distinguishes similar student mistakes and assigns the correct supported misconception.
2. **Re-quiz validity:** Whether one successful re-quiz is enough evidence that the misconception is actually resolved rather than temporarily answered correctly.
3. **Mentor threshold:** Whether two failed autonomous remediation attempts is the right point to involve a human.

## 16. Claims to verify

| claim | how to check | checked? |
|---|---|---|
| The model can return structured diagnosis/evaluation JSON | Run live M1/M2/M3 cases and inspect outputs | Yes |
| A failed evaluation causes a different teaching strategy | Run a misconception with two failed re-quizzes | Yes |
| Student state persists between encounters | Run the same student twice and compare strategy selection | Yes |
| The mentor decision changes the final flow | Test `resolve`, `continue`, and `retry` paths | Partially |
| Empty model responses do not produce the previous `.strip()` crash | Reproduce an empty response and inspect error handling | Yes |

## Final checklist

- [x] End-to-end fake pipeline exists.
- [x] Live misconception loop tested.
- [x] Backward `EVALUATE → TEACH` transition demonstrated.
- [x] Different remediation strategy demonstrated.
- [x] Persistent second encounter demonstrated.
- [x] Mentor escalation demonstrated.
- [x] Structured model output is checked rather than blindly trusted.
- [x] Project excludes `.env`, `.venv`, `__pycache__`, and `student_state.json` from Git tracking.
