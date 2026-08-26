"""
Sends a PR diff to an LLM and parses the structured JSON response back
into (summary, issues, suggestions). Supports two providers:

- Groq (default): OpenAI-compatible API, generous free tier, very fast.
- Anthropic: used if AI_PROVIDER=anthropic and ANTHROPIC_API_KEY is set.

Kept as plain functions (no class state) so it's trivially unit-testable.
"""
import json
import httpx

from app.config import get_settings

settings = get_settings()

REVIEW_PROMPT_TEMPLATE = """You are an expert code reviewer. Review the following pull request diff.

Diff:
{diff}

Respond ONLY with valid JSON in this exact shape, nothing else:
{{
  "summary": "one or two sentence overview",
  "issues": [{{"line": null, "severity": "warning", "message": "..."}}],
  "suggestions": ["..."]
}}
"""


def build_review_prompt(diff: str) -> str:
    # Truncate to keep token usage predictable on very large diffs.
    truncated = diff[:15000]
    return REVIEW_PROMPT_TEMPLATE.format(diff=truncated)


def parse_ai_response(raw_text: str) -> dict:
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()
    
    # Extract just the JSON object, in case there's stray text before/after
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]
    
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI response was not valid JSON: {exc}") from exc

    data.setdefault("summary", "")
    data.setdefault("issues", [])
    data.setdefault("suggestions", [])
    return data

async def _call_groq(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.groq_api_key}",
            },
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 1024,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]


async def _call_anthropic(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        data = response.json()

    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    if not text_blocks:
        raise ValueError("No text content returned from AI API")
    return text_blocks[0]


async def review_diff(diff: str) -> dict:
    provider = settings.ai_provider.lower()

    has_key = (provider == "groq" and settings.groq_api_key) or (
        provider == "anthropic" and settings.anthropic_api_key
    )
    if not has_key:
        return {
            "summary": f"AI review skipped - no API key configured for provider '{provider}'.",
            "issues": [],
            "suggestions": [],
        }

    prompt = build_review_prompt(diff)

    if provider == "groq":
        raw_text = await _call_groq(prompt)
    elif provider == "anthropic":
        raw_text = await _call_anthropic(prompt)
    else:
        raise ValueError(f"Unknown AI_PROVIDER: {provider}")

    return parse_ai_response(raw_text)
