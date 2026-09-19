# CEG ASTRA --- Agent-a-Thon Day 1 Progress Report

**Project:** CEG ASTRA --- Misconception Loop\
**Hackathon:** Agent-a-Thon 2026\
**Day:** Day 1\
**Date:** 19 September 2026\
**Focus:** Build and validate the first working misconception loop

------------------------------------------------------------------------

## 1. Day 1 Objective

The objective for Day 1 was to implement a working end-to-end tutoring
loop for one narrow topic:

``` text
Quiz → Diagnose → Teach → Re-quiz → Evaluate → Pass / Retry
```

The selected topic for the initial slice is **Python Lists**.

The system is designed to identify why a student's answer is wrong
rather than only marking it incorrect.

------------------------------------------------------------------------

## 2. What Was Implemented

### 2.1 Question and misconception model

A small hand-written question bank was established for Python Lists.

The initial supported misconceptions are:

-   **M1 --- `append()` vs `extend()`**
-   **M2 --- Index vs value**
-   **M3 --- Slice boundaries**

Each question is associated with the relevant misconception and includes
the information required to evaluate the student's response.

### 2.2 Diagnosis agent

The diagnosis step analyzes the student's answer and produces a
structured diagnosis containing information such as:

-   whether the answer is correct,
-   the identified misconception,
-   confidence,
-   reasoning for the diagnosis.

The diagnosis scope is restricted to the supported misconception set.

### 2.3 Teaching agent

A separate teaching step provides targeted remediation for the diagnosed
misconception.

Teaching strategies are selected programmatically so that the system can
avoid repeatedly using the same strategy for the same student and
misconception.

Examples of strategies include:

-   code comparison,
-   analogy,
-   step-by-step tracing.

### 2.4 Re-quiz and evaluation

After teaching, the student receives a different question testing the
same misconception.

The evaluation agent determines whether the student's new response
demonstrates that the misconception has been addressed.

The result controls the next workflow transition.

### 2.5 Backward agentic loop

The central Day 1 agentic behavior was implemented:

``` text
TEACH
  ↓
RE-QUIZ
  ↓
EVALUATE
  ↓
FAIL
  ↓
TEACH AGAIN
```

A failed re-quiz therefore sends the workflow backward instead of simply
moving to the next question.

This allows the tutor to attempt another remediation strategy.

### 2.6 Controlled retry and mentor escalation

Autonomous remediation is bounded by a retry limit.

After the allowed remediation attempts are exhausted, the system moves
to mentor review rather than continuing indefinitely.

This provides an explicit stopping condition for the autonomous tutor.

### 2.7 Persistent student state

Student state is stored in JSON so that progress can be retained between
encounters.

The stored information includes items such as:

-   student ID,
-   answers,
-   diagnosed misconceptions,
-   teaching attempts,
-   strategies used,
-   evaluations,
-   misconception status,
-   mentor decisions.

This establishes the foundation for returning-student behavior in Day 2.

### 2.8 Separation of agent reasoning and workflow control

The system separates LLM reasoning from deterministic workflow control.

The LLM is responsible for tasks such as:

-   diagnosing misconceptions,
-   generating explanations,
-   evaluating remediation answers.

Python controls:

-   state transitions,
-   question selection,
-   retry limits,
-   strategy history,
-   persistent state,
-   mentor escalation,
-   model-call limits.

This prevents the model from bypassing the intended tutoring workflow.

------------------------------------------------------------------------

## 3. Day 1 State Machine

The implemented workflow is:

``` text
QUIZ
  ↓
DIAGNOSE
  ↓
 ┌───────────────┐
 │   Correct?    │
 └───────┬───────┘
      Yes│       │No
         ↓       ↓
  NEXT QUESTION  TEACH
                   ↓
                RE-QUIZ
                   ↓
                EVALUATE
                /      \
             Pass       Fail
              ↓           ↓
        NEXT QUESTION    TEACH
                           ↓
                        RE-QUIZ
                           ↓
                     Retry limit
                           ↓
                         MENTOR
```

The key Day 1 proof point is the **backward edge from evaluation failure
to teaching**.

------------------------------------------------------------------------

## 4. Testing and Validation

The implementation was designed to support both:

### Fake state-machine testing

`demo_fake.py` allows the workflow to be exercised without a live API
key.

This verifies the state-machine behavior independently from model
availability.

### Live model execution

`main.py` connects the workflow to the LLM through the configured
OpenRouter interface.

A live run can therefore demonstrate:

1.  a student's incorrect answer,
2.  misconception diagnosis,
3.  targeted teaching,
4.  a re-quiz,
5.  evaluation,
6.  a retry with a different strategy, and
7.  mentor escalation after repeated failure.

------------------------------------------------------------------------

## 5. Day 1 Evidence

A representative M1 scenario demonstrates the intended behavior:

``` text
Student answers an append()/extend() question incorrectly
        ↓
Diagnosis identifies M1
        ↓
First teaching strategy: code comparison
        ↓
Student attempts re-quiz
        ↓
Evaluation = fail
        ↓
Workflow returns to TEACH
        ↓
Second strategy: analogy
        ↓
Student receives another re-quiz
```

The system records the intermediate steps in persistent student state,
making the workflow inspectable rather than treating the interaction as
a single opaque model response.

------------------------------------------------------------------------

## 6. Engineering Decisions

The following decisions were made during Day 1:

### Narrow scope

The first implementation is deliberately restricted to Python Lists
rather than attempting to build a general-purpose tutor.

### Explicit misconception set

The system uses a small supported misconception set instead of allowing
the model to invent arbitrary misconception categories.

### Deterministic workflow

State transitions and retry limits are controlled by Python rather than
by free-form LLM output.

### Persistent JSON state

A JSON file is sufficient for the two-day prototype and makes student
history easy to inspect.

### Bounded autonomy

The tutor has a defined remediation limit and can stop for mentor review
instead of retrying indefinitely.

------------------------------------------------------------------------

## 7. Day 1 Outcome

By the end of Day 1, the project had a working prototype of the core
Misconception Loop:

> **The system can receive a student's answer, diagnose a supported
> misconception, provide targeted remediation, re-test the student,
> evaluate the result, and send the workflow backward for another
> remediation attempt when the student still struggles.**

This establishes the core agentic slice required before expanding the
system with additional Day 2 evidence and testing.

------------------------------------------------------------------------

## 8. Day 2 Focus

The Day 1 implementation provides the foundation for Day 2 work:

-   strengthen the multi-misconception behavior within Python Lists,
-   demonstrate returning-student history,
-   run the system with three real testers,
-   observe actual user behavior,
-   make a change based on testing evidence,
-   and prepare the final demonstration.

------------------------------------------------------------------------

## 9. Repository / Development Notes

The project is structured around:

``` text
main.py
flow.py
agents.py
llm.py
store.py
questions.json
misconceptions.json
prompts/
demo_fake.py
```

The repository also contains the pre-event asset declaration required
for the hackathon.

New event-time work is kept visible through Git history.

------------------------------------------------------------------------

**Day 1 status: Core misconception-loop prototype implemented and ready
for Day 2 user testing.**
