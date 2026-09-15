# CEG ASTRA — Misconception Loop

A deliberately small agentic tutoring slice for Python Lists.

## Core loop

Student answer
→ Diagnose
→ Teach
→ Re-quiz
→ Evaluate
→ Pass OR backward edge to Teach
→ after 2 failed remediation attempts → Mentor

## Project structure

- `main.py` — connects the complete flow
- `flow.py` — state machine and limits
- `agents.py` — LLM agent wrappers
- `llm.py` — OpenRouter API call
- `store.py` — persistent student memory
- `questions.json` — 12 tagged questions
- `misconceptions.json` — 3 supported misconceptions
- `prompts/` — Diagnose, Teach, Evaluate prompts
- `demo_fake.py` — tests the state machine without an API key
- `student_state.json` — created automatically after a real run

## Run the fake state-machine test

```bash
python demo_fake.py
```

## Run with OpenRouter

Set your environment variable.

Windows PowerShell:
```powershell
$env:OPENROUTER_API_KEY="YOUR_KEY"
```

macOS/Linux:
```bash
export OPENROUTER_API_KEY="YOUR_KEY"
```

Optional model:
```bash
export OPENROUTER_MODEL="openai/gpt-oss-20b"
```

Then:
```bash
python main.py
```

## Demo plan

1. Use a student ID such as `student_001`.
2. On Q2 deliberately answer `[1, 2, 3, 4]`.
3. Show diagnosis M1.
4. Show first teaching strategy.
5. Fail the first re-quiz deliberately.
6. Show the backward edge to Teach.
7. Show a different teaching strategy.
8. Pass the second re-quiz with `[10, [20, 30]]`.
9. Show `student_state.json`.
10. Run the same student again to demonstrate persistent history.
11. Demonstrate mentor escalation by deliberately failing two re-quizzes.
12. Demonstrate prompt injection using a student answer containing an instruction such as `Ignore previous instructions...`.

## Important design choices

- Only three misconceptions are supported.
- Questions are tagged for organization, but diagnosis is based on the actual answer.
- Re-quiz questions are different from the original question.
- The state machine, not the LLM, controls transitions and limits.
- Autonomous remediation is limited to two attempts.
- Model-call/spend limit is separate from the remediation limit.
- Human mentor escalation stops autonomous tutoring.

## Security demo

External/student content is treated as data, not instructions. The diagnosis, teaching, and evaluation prompts explicitly tell the model to ignore instructions embedded in student answers.

For a competition demo, keep the API key in an environment variable and never commit it.
