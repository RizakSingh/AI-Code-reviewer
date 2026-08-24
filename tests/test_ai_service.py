import pytest

from app.services.ai_service import parse_ai_response, build_review_prompt


def test_parse_clean_json():
    raw = '{"summary": "Looks good", "issues": [], "suggestions": ["Add tests"]}'
    result = parse_ai_response(raw)
    assert result["summary"] == "Looks good"
    assert result["suggestions"] == ["Add tests"]


def test_parse_json_with_code_fences():
    raw = '```json\n{"summary": "OK", "issues": [], "suggestions": []}\n```'
    result = parse_ai_response(raw)
    assert result["summary"] == "OK"


def test_parse_fills_missing_keys_with_defaults():
    raw = '{"summary": "Partial response"}'
    result = parse_ai_response(raw)
    assert result["issues"] == []
    assert result["suggestions"] == []


def test_parse_invalid_json_raises():
    with pytest.raises(ValueError):
        parse_ai_response("this is not json at all")


def test_build_review_prompt_includes_diff():
    prompt = build_review_prompt("+ added this line")
    assert "+ added this line" in prompt


def test_build_review_prompt_truncates_large_diffs():
    huge_diff = "x" * 50000
    prompt = build_review_prompt(huge_diff)
    # Should be truncated to 15000 chars + template overhead, not the full 50000
    assert len(prompt) < 20000
