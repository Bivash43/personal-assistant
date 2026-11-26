from datetime import date

from personal_assistant.prompts import RULES, build_system_prompt, numbered


def test_prompt_contains_todays_date() -> None:
    prompt = build_system_prompt(date(2026, 11, 26))

    assert "Thursday 26 November 2026" in prompt


def test_prompt_contains_every_rule() -> None:
    prompt = build_system_prompt(date.today())

    for r in RULES:
        assert r in prompt


def test_numbered_counts_from_one() -> None:
    assert numbered(["a", "b", "c"]) == "1. a\n2. b\n3. c"


def test_prompt_contains_all_rules_numbered() -> None:
    prompt = build_system_prompt(date(2026, 11, 26))

    assert numbered(RULES) in prompt
