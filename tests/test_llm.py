import pytest
from pathlib import Path
from personal_assistant.config import Settings
from personal_assistant.llm import get_chat_model 
from langchain_ollama import ChatOllama

def test_ollama_provider_returns_chat_ollama(monkeypatch: pytest.MonkeyPatch, tmp_path: Path)->None:
    monkeypatch.chdir(tmp_path)
    s = Settings()
    result = get_chat_model(s)
    assert isinstance(result, ChatOllama)
    
def test_not_implemented_provider_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path)->None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASSISTANT_LLM_PROVIDER" , "openai")
    s = Settings()
    
    with pytest.raises(NotImplementedError):
        get_chat_model(s)