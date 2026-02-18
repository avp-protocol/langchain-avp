<p align="center">
  <img src="https://raw.githubusercontent.com/avp-protocol/spec/main/assets/avp-shield.svg" alt="AVP Shield" width="80" />
</p>

<h1 align="center">langchain-avp</h1>

<p align="center">
  <strong>LangChain secret manager integration for AVP</strong><br>
  Drop-in replacement · All LLM providers · Hardware security
</p>

<p align="center">
  <a href="https://pypi.org/project/langchain-avp/"><img src="https://img.shields.io/pypi/v/langchain-avp?style=flat-square&color=00D4AA" alt="PyPI" /></a>
  <a href="https://github.com/avp-protocol/langchain-avp/actions"><img src="https://img.shields.io/github/actions/workflow/status/avp-protocol/langchain-avp/ci.yml?style=flat-square" alt="CI" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-blue?style=flat-square" alt="License" /></a>
</p>

---

## Overview

`langchain-avp` provides AVP integration for LangChain. Replace insecure `.env` files with hardware-grade credential storage — no code changes required.

## Installation

```bash
pip install langchain-avp
```

## Quick Start

### Before (insecure .env)

```python
from langchain_anthropic import ChatAnthropic
import os

# ❌ API key in plaintext .env file
llm = ChatAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
```

### After (secure AVP vault)

```python
from langchain_anthropic import ChatAnthropic
from langchain_avp import AVPSecretManager

# ✅ API key in hardware-secured vault
secrets = AVPSecretManager("avp.toml")
llm = ChatAnthropic(api_key=secrets.get("anthropic_api_key"))
```

## Automatic Environment Loading

Load all secrets into environment variables at startup:

```python
from langchain_avp import load_secrets

# Load secrets into os.environ
load_secrets("avp.toml", [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "PINECONE_API_KEY",
])

# Now use LangChain normally — it reads from environment
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic()  # Automatically uses ANTHROPIC_API_KEY
```

## Migration from .env

```bash
# Step 1: Import existing .env into AVP
avp import .env --backend keychain

# Step 2: Update your code
# Replace: load_dotenv()
# With:    from langchain_avp import load_secrets; load_secrets("avp.toml")

# Step 3: Delete insecure .env file
rm .env
```

## Provider-Specific Examples

### Anthropic

```python
from langchain_anthropic import ChatAnthropic
from langchain_avp import AVPSecretManager

secrets = AVPSecretManager("avp.toml")
llm = ChatAnthropic(api_key=secrets.get("anthropic_api_key"))
```

### OpenAI

```python
from langchain_openai import ChatOpenAI
from langchain_avp import AVPSecretManager

secrets = AVPSecretManager("avp.toml")
llm = ChatOpenAI(api_key=secrets.get("openai_api_key"))
```

### Multiple Providers

```python
from langchain_avp import AVPSecretManager

secrets = AVPSecretManager("avp.toml")

anthropic_llm = ChatAnthropic(api_key=secrets.get("anthropic_api_key"))
openai_llm = ChatOpenAI(api_key=secrets.get("openai_api_key"))
pinecone = Pinecone(api_key=secrets.get("pinecone_api_key"))
```

## Backend Selection

```python
from langchain_avp import AVPSecretManager, Backend

# OS Keychain (recommended)
secrets = AVPSecretManager(backend=Backend.KEYCHAIN)

# Hardware secure element (maximum security)
secrets = AVPSecretManager(backend=Backend.HARDWARE)

# Remote vault (team environments)
secrets = AVPSecretManager(
    backend=Backend.REMOTE,
    url="https://vault.company.com"
)
```

## With LangChain Agents

```python
from langchain.agents import initialize_agent
from langchain_avp import AVPSecretManager

secrets = AVPSecretManager("avp.toml")

# All tool credentials from AVP
tools = [
    SerpAPIWrapper(serpapi_api_key=secrets.get("serpapi_key")),
    WikipediaQueryRun(),
]

agent = initialize_agent(
    tools=tools,
    llm=ChatAnthropic(api_key=secrets.get("anthropic_api_key")),
)
```

## Security Comparison

| Method | Infostealer | Git Leak | Host Compromise |
|--------|:-----------:|:--------:|:---------------:|
| .env file | ✗ | ✗ | ✗ |
| Environment vars | ✗ | ✓ | ✗ |
| AVP Keychain | ✓ | ✓ | ✗ |
| AVP Hardware | ✓ | ✓ | ✓ |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

<p align="center">
  <a href="https://github.com/avp-protocol/spec">AVP Specification</a> ·
  <a href="https://python.langchain.com/">LangChain</a>
</p>
