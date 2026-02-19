"""LangChain integration for Agent Vault Protocol."""

from langchain_avp.credential_provider import AVPCredentialProvider
from langchain_avp.callbacks import AVPCredentialCallback
from langchain_avp.utils import get_llm_with_avp, load_credentials

__all__ = [
    "AVPCredentialProvider",
    "AVPCredentialCallback",
    "get_llm_with_avp",
    "load_credentials",
]

__version__ = "0.1.0"
