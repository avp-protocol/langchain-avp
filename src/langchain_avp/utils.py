"""Utility functions for LangChain-AVP integration."""

from typing import Optional, Dict, Any, Type
import os

from langchain_avp.credential_provider import AVPCredentialProvider


def load_credentials(
    vault_path: str,
    password: Optional[str] = None,
    workspace: str = "langchain",
    env_vars: Optional[Dict[str, str]] = None,
) -> AVPCredentialProvider:
    """
    Load credentials from AVP vault and optionally set environment variables.

    Args:
        vault_path: Path to the encrypted vault file.
        password: Vault password (will prompt if not provided).
        workspace: AVP workspace name.
        env_vars: Mapping of env var names to credential names.
                  e.g., {"ANTHROPIC_API_KEY": "anthropic_api_key"}

    Returns:
        AVPCredentialProvider instance.

    Example:
        >>> credentials = load_credentials(
        ...     "vault.enc",
        ...     env_vars={"ANTHROPIC_API_KEY": "anthropic_api_key"}
        ... )
        >>> # Now os.environ["ANTHROPIC_API_KEY"] is set
    """
    provider = AVPCredentialProvider(
        vault_path=vault_path,
        password=password,
        workspace=workspace,
    )

    if env_vars:
        for env_name, cred_name in env_vars.items():
            value = provider.get(cred_name)
            if value:
                os.environ[env_name] = value

    return provider


def get_llm_with_avp(
    provider: str,
    credentials: AVPCredentialProvider,
    model: Optional[str] = None,
    **kwargs: Any,
):
    """
    Create an LLM instance with credentials from AVP.

    Args:
        provider: LLM provider name (anthropic, openai, etc.)
        credentials: AVPCredentialProvider instance.
        model: Optional model name override.
        **kwargs: Additional arguments passed to the LLM constructor.

    Returns:
        LangChain LLM instance.

    Example:
        >>> credentials = AVPCredentialProvider("vault.enc")
        >>> llm = get_llm_with_avp("anthropic", credentials)
        >>> response = llm.invoke("Hello!")
    """
    api_key = credentials.get_api_key(provider)
    if not api_key:
        raise ValueError(f"No API key found for provider: {provider}")

    provider = provider.lower()

    if provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("Install langchain-anthropic: pip install langchain-anthropic")

        return ChatAnthropic(
            api_key=api_key,
            model=model or "claude-3-haiku-20240307",
            **kwargs,
        )

    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("Install langchain-openai: pip install langchain-openai")

        return ChatOpenAI(
            api_key=api_key,
            model=model or "gpt-3.5-turbo",
            **kwargs,
        )

    elif provider == "cohere":
        try:
            from langchain_cohere import ChatCohere
        except ImportError:
            raise ImportError("Install langchain-cohere: pip install langchain-cohere")

        return ChatCohere(
            cohere_api_key=api_key,
            model=model or "command",
            **kwargs,
        )

    elif provider == "mistral":
        try:
            from langchain_mistralai import ChatMistralAI
        except ImportError:
            raise ImportError("Install langchain-mistralai: pip install langchain-mistralai")

        return ChatMistralAI(
            api_key=api_key,
            model=model or "mistral-small-latest",
            **kwargs,
        )

    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Supported: anthropic, openai, cohere, mistral"
        )
