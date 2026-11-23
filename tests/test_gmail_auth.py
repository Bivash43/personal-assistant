from pathlib import Path

from personal_assistant.gmail.auth import _save_token


class FakeCreds:
    def to_json(self) -> str:
        return '{"token": "abc"}'


def test_save_token_writes_to_given_path(tmp_path: Path) -> None:
    token_path = tmp_path / "nested" / "token.json"

    _save_token(FakeCreds(), token_path)  # type: ignore[arg-type]

    assert token_path.exists()
    assert token_path.read_text(encoding="utf-8") == '{"token": "abc"}'
    assert token_path.stat().st_mode & 0o777 == 0o600


def test_save_token_tightens_existing_permissions(tmp_path: Path) -> None:
    token_path = tmp_path / "token.json"
    token_path.write_text("old")
    token_path.chmod(0o644)  # world-readable, like a careless earlier save

    _save_token(FakeCreds(), token_path)  # type: ignore[arg-type]

    assert token_path.stat().st_mode & 0o777 == 0o600
    assert token_path.read_text(encoding="utf-8") == '{"token": "abc"}'
