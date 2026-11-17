from langchain_core.language_models.chat_models import BaseChatModel

from personal_assistant.config import Settings


def get_chat_model(settings: Settings) -> BaseChatModel:
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.ollama_model, base_url=settings.ollama_base_url, temperature=0
        )
    else:
        raise NotImplementedError(f"Provider '{settings.llm_provider}' is not wired up yet")
