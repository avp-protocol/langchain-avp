"""LangChain callbacks for AVP credential auditing."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class AVPCredentialCallback(BaseCallbackHandler):
    """
    LangChain callback handler that logs credential usage for auditing.

    Tracks which credentials are accessed during LangChain operations.

    Example:
        >>> callback = AVPCredentialCallback(credentials)
        >>> llm = ChatAnthropic(callbacks=[callback])
        >>> llm.invoke("Hello")
        >>> print(callback.get_audit_log())
    """

    def __init__(self, credential_provider: Any = None):
        """
        Initialize the callback handler.

        Args:
            credential_provider: Optional AVPCredentialProvider for logging.
        """
        self.credential_provider = credential_provider
        self._audit_log: List[Dict[str, Any]] = []
        self._current_run: Optional[str] = None

    def _log(self, event: str, metadata: Optional[Dict[str, Any]] = None):
        """Log an event to the audit log."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "run_id": self._current_run,
        }
        if metadata:
            entry["metadata"] = metadata
        self._audit_log.append(entry)

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts running."""
        self._current_run = str(run_id) if run_id else None

        # Extract model info
        model = serialized.get("kwargs", {}).get("model", "unknown")
        provider = serialized.get("id", ["unknown"])[-1] if serialized.get("id") else "unknown"

        self._log("llm_start", {
            "provider": provider,
            "model": model,
            "prompt_count": len(prompts),
        })

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM finishes running."""
        token_usage = {}
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})

        self._log("llm_end", {
            "generations": len(response.generations),
            "token_usage": token_usage,
        })
        self._current_run = None

    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM errors."""
        self._log("llm_error", {
            "error": str(error),
            "error_type": type(error).__name__,
        })
        self._current_run = None

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the full audit log."""
        return self._audit_log.copy()

    def clear_audit_log(self):
        """Clear the audit log."""
        self._audit_log = []

    def print_audit_log(self):
        """Print the audit log in a readable format."""
        print("\nLangChain-AVP Audit Log:")
        print("-" * 60)
        for entry in self._audit_log:
            meta = entry.get("metadata", {})
            meta_str = ", ".join(f"{k}={v}" for k, v in meta.items())
            print(f"  {entry['timestamp']} | {entry['event']}: {meta_str}")
        print("-" * 60)
