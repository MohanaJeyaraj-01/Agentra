# PRE-EVENT-ASSETS

## Agentathon 2026 — Agentra / Misconception Loop

This file declares the work and assets that existed before the Agentathon event and are being brought into the event repository. The purpose is transparency about what was already available before event-day development.

---

## 1. Prior Code

The following code existed before the event:

- **Agentra / Misconception Loop** — an earlier implementation of the agentic tutoring project.
- **`Agentra-main.zip`** — the pre-existing project/codebase from which the current hackathon work is being continued.
- Existing implementation of the misconception-loop workflow, supporting Python code, project structure, and related configuration/documentation that were present before the event.

The current hackathon implementation is therefore an extension/refinement of an existing project rather than a project created entirely from an empty repository during the event.

---

## 2. Prior Prompts / Agent Definitions

The following project design material existed before the event:

- Misconception Loop / Agentra agent specification.
- Agent behavior and workflow definitions for:
  - diagnosing a student's misconception,
  - selecting targeted remediation,
  - evaluating the student's re-attempt,
  - repeating remediation when necessary,
  - escalating to a human mentor after the autonomous retry limit,
  - maintaining student state across encounters.
- Prompt/design material used to guide diagnosis, teaching, evaluation, and strategy selection.

---

## 3. Prior Evaluation Sets / Test Scenarios

Pre-event testing and evaluation scenarios existed for the misconception-loop behavior, including:

1. Present a Python question.
2. Receive an incorrect student answer.
3. Diagnose the supported misconception.
4. Provide targeted teaching/remediation.
5. Re-quiz the student.
6. Evaluate the new response.
7. If the misconception persists, send the flow back to teaching with a different remediation strategy.
8. Escalate to a mentor after the defined autonomous retry limit.
9. Run the same student again and use persisted state/strategy history.

These scenarios were part of the project design/testing work before the event.

---

## 4. Prior Datasets

**No external dataset was gathered specifically for the start of this event.**

The project uses its pre-existing question/misconception records and test material that were already part of the project before the event.

If additional questions, misconception records, or other data are created during the event, those additions are considered event-time work and are not being declared as pre-event assets.

---

## 5. Prior Libraries / Dependencies

The existing project already contained its required software dependencies before the event.

The pre-existing implementation uses its existing Python/runtime dependencies and project libraries. These dependencies are part of the brought-in codebase rather than newly introduced solely to represent the project as pre-existing.

Any new library or dependency introduced during the event will be treated as event-time work and recorded through the repository history.

---

## 6. Prior Documentation / Specifications

The following documentation/specification work existed before the event:

- Agentra / Misconception Loop project specification.
- Agent flow and state-transition design.
- Misconception definitions and supported misconception scope.
- Teaching/remediation strategy design.
- Evaluation and persistence behavior definitions.
- Existing demo/test scenarios.

---

## 7. What Is Being Built During the Event

The hackathon team may modify, extend, debug, integrate, test, and improve the pre-existing project.

Examples of event-time work include:

- new or modified agent behavior,
- new prompts,
- new questions or misconception cases,
- new integrations,
- UI changes,
- additional evaluation,
- bug fixes,
- performance improvements,
- documentation updates,
- new dependencies,
- and other implementation changes made during the event.

These changes should remain visible in the Git history.

---

## 8. Transparency Declaration

The assets above are being declared because they existed before the event. Reusing them is intentional.

No event-time work is being represented as pre-existing work. New additions made during the hackathon will be distinguishable through the repository's commit history.

---

**Declaration date:** 19 September 2026
