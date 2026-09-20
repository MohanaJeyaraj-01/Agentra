import json
import os
import urllib.request
import urllib.error


API_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_llm(system_prompt, user_prompt, model=None):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    model = model or os.getenv(
        "OPENROUTER_MODEL",
        "openai/gpt-oss-20b"
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.2
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "CEG ASTRA Misconception Loop"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            body = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as e:
        detail = e.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"OpenRouter HTTP {e.code}: {detail}"
        ) from e

    except urllib.error.URLError as e:
        raise RuntimeError(
            "Unable to connect to the AI service. "
            "Please check your internet connection "
            "and try again."
        ) from e

    except TimeoutError as e:
        raise RuntimeError(
            "The AI request timed out. "
            "Please check your internet connection "
            "and try again."
        ) from e

    return body["choices"][0]["message"]["content"]


def parse_json(text):
    if text is None:
        raise RuntimeError(
            "LLM returned an empty response."
        )

    text = text.strip()

    if not text:
        raise RuntimeError(
            "LLM returned a blank response."
        )

    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"LLM returned invalid JSON:\n{text}"
        ) from e
