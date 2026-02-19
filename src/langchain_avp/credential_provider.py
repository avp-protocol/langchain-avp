"""AVP Credential Provider for LangChain."""

from typing import Optional, Dict, Any, List
from pathlib import Path
import getpass

from avp import AVPClient
from avp.backends import FileBackend, MemoryBackend


class AVPCredentialProvider:
    """
    Credential provider that integrates AVP with LangChain.

    Provides secure credential storage and retrieval for LangChain applications.

    Example:
        >>> credentials = AVPCredentialProvider("vault.enc", password="secret")
        >>> api_key = credentials.get("anthropic_api_key")
        >>> llm = ChatAnthropic(api_key=api_key)
    """

    def __init__(
        self,
        vault_path: Optional[str] = None,
        password: Optional[str] = None,
        workspace: str = "langchain",
        backend: Optional[Any] = None,
    ):
        """
        Initialize the AVP credential provider.

        Args:
            vault_path: Path to the encrypted vault file. If None, uses in-memory backend.
            password: Vault password. If None and vault_path is provided, will prompt.
            workspace: AVP workspace name for credential isolation.
            backend: Custom AVP backend. If provided, vault_path and password are ignored.
        """
        self._workspace = workspace
        self._client: Optional[AVPClient] = None
        self._session_id: Optional[str] = None

        if backend is not None:
            self._backend = backend
        elif vault_path is not None:
            if password is None:
                password = getpass.getpass(f"Enter password for {vault_path}: ")
            self._backend = FileBackend(vault_path, password)
        else:
            self._backend = MemoryBackend()

        self._connect()

    def _connect(self):
        """Connect to the AVP vault."""
        self._client = AVPClient(self._backend)
        session = self._client.authenticate(workspace=self._workspace)
        self._session_id = session.session_id

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a credential from the vault.

        Args:
            name: Name of the credential.
            default: Default value if credential not found.

        Returns:
            The credential value or default.
        """
        try:
            result = self._client.retrieve(self._session_id, name)
            return result.value.decode()
        except Exception:
            return default

    def set(self, name: str, value: str, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Store a credential in the vault.

        Args:
            name: Name of the credential.
            value: The credential value.
            labels: Optional metadata labels.
        """
        self._client.store(
            self._session_id,
            name,
            value.encode(),
            labels=labels
        )

    def delete(self, name: str) -> bool:
        """
        Delete a credential from the vault.

        Args:
            name: Name of the credential.

        Returns:
            True if deleted, False if not found.
        """
        result = self._client.delete(self._session_id, name)
        return result.deleted

    def list(self, labels: Optional[Dict[str, str]] = None) -> List[str]:
        """
        List all credentials in the workspace.

        Args:
            labels: Optional label filter.

        Returns:
            List of credential names.
        """
        result = self._client.list_secrets(self._session_id, filter_labels=labels)
        return [s.name for s in result.secrets]

    def rotate(self, name: str, new_value: str) -> None:
        """
        Rotate a credential (update with version tracking).

        Args:
            name: Name of the credential.
            new_value: New credential value.
        """
        self._client.rotate(self._session_id, name, new_value.encode())

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get an API key for a specific provider.

        Convenience method that maps provider names to credential names.

        Args:
            provider: Provider name (anthropic, openai, cohere, etc.)

        Returns:
            The API key or None.
        """
        key_mapping = {
            "anthropic": "anthropic_api_key",
            "openai": "openai_api_key",
            "cohere": "cohere_api_key",
            "huggingface": "huggingface_api_key",
            "google": "google_api_key",
            "mistral": "mistral_api_key",
        }
        credential_name = key_mapping.get(provider.lower(), f"{provider.lower()}_api_key")
        return self.get(credential_name)

    def close(self):
        """Close the vault connection."""
        if self._client:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
