"""Tests for AVPCredentialProvider."""

import pytest
from langchain_avp import AVPCredentialProvider


class TestAVPCredentialProvider:
    """Test suite for AVPCredentialProvider."""

    def test_memory_backend(self):
        """Test with in-memory backend."""
        provider = AVPCredentialProvider()

        # Store and retrieve
        provider.set("test_key", "test_value")
        assert provider.get("test_key") == "test_value"

        # List credentials
        creds = provider.list()
        assert "test_key" in creds

        # Delete
        assert provider.delete("test_key") is True
        assert provider.get("test_key") is None

        provider.close()

    def test_get_default(self):
        """Test get with default value."""
        provider = AVPCredentialProvider()

        result = provider.get("nonexistent", default="default_value")
        assert result == "default_value"

        provider.close()

    def test_get_api_key(self):
        """Test get_api_key convenience method."""
        provider = AVPCredentialProvider()

        provider.set("anthropic_api_key", "sk-ant-test")
        provider.set("openai_api_key", "sk-test")

        assert provider.get_api_key("anthropic") == "sk-ant-test"
        assert provider.get_api_key("openai") == "sk-test"
        assert provider.get_api_key("unknown") is None

        provider.close()

    def test_context_manager(self):
        """Test context manager usage."""
        with AVPCredentialProvider() as provider:
            provider.set("ctx_key", "ctx_value")
            assert provider.get("ctx_key") == "ctx_value"

    def test_labels(self):
        """Test credentials with labels."""
        provider = AVPCredentialProvider()

        provider.set("prod_key", "prod_value", labels={"env": "production"})
        provider.set("dev_key", "dev_value", labels={"env": "development"})

        # List with filter
        prod_creds = provider.list(labels={"env": "production"})
        assert "prod_key" in prod_creds
        assert "dev_key" not in prod_creds

        provider.close()

    def test_rotate(self):
        """Test credential rotation."""
        provider = AVPCredentialProvider()

        provider.set("rotate_key", "v1")
        assert provider.get("rotate_key") == "v1"

        provider.rotate("rotate_key", "v2")
        assert provider.get("rotate_key") == "v2"

        provider.close()
