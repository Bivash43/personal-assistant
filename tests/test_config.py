from pathlib import Path

import pytest
from pydantic import ValidationError

from personal_assistant.config import Settings


def test_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:

    # Arrange: run inside an empty temporary folder
    monkeypatch.chdir(tmp_path)

    # Act: create settings with no ooverrides
    s = Settings()

    # Assert: the defaults are what we expect
    assert s.llm_provider == "ollama"
    assert s.db_path == Path("data") / "assistant.db"


def test_data_dir_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASSISTANT_DATA_DIR", "elsewhere")

    s = Settings()

    assert s.db_path == Path("elsewhere") / "assistant.db"


def test_invalid_provider_is_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASSISTANT_LLM_PROVIDER", "banana")

    with pytest.raises(ValidationError):
        Settings()
