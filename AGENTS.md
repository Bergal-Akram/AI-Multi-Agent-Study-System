# 🤖 AI Agent Instructions & Project Context

This document provides context and rules for AI Coding Assistants (Cursor, Copilot, Gemini, etc.) to ensure code generation aligns with the **SMA Multi-Agent Study System** architecture.

---

## 🎯 Project Intent

A Distributed Multi-Agent System (MAS) built on **SPADE (Smart Python Agent Development Environment)**. The system automates study planning by orchestrating specialized agents over **XMPP**.

## 🏗️ Architecture Rules (CRITICAL)

1. **Base Class**: Every new agent **MUST** inherit from `spade.agent.Agent`.
2. **Behavior Pattern**: Use `spade.behaviour.CyclicBehaviour` for workers and `OneShotBehaviour` for initialization/proxies.
3. **Communication**: All inter-agent communication must follow **FIPA-ACL standards** using `spade.message.Message`.
   - Use `.set_metadata("performative", "request")` for tasks.
   - Use `.set_metadata("performative", "inform")` for data delivery.
4. **Environment**: Never hardcode credentials. Use `os.getenv()` and `load_dotenv()`.

## 🧠 LLM Usage Guidelines

- **Planner Agent**: Uses `llama-3.3-70b-versatile`.
  - _Temperature_: 0.5 (Balanced reasoning).
  - _Goal_: High-level pedagogical strategy.
- **Resourcer Agent**: Uses `llama-3.1-8b-instant`.
  - _Temperature_: 0.1 (Strict extraction).
  - _Goal_: Parsing JSON from search results without hallucinations.

## 📂 Codebase Map

- `app/agents/`: Core logic for all agents.
- `main.py`: Connection management and XMPP socket lifecycle.
- `.env`: Source of truth for JIDs and API keys.

## 🛠️ Code Style Preferences

- **Async/Await**: SPADE is an asynchronous framework. Use `await self.receive()` and `await self.send()`.
- **Typing**: Use Python type hints (e.g., `msg: Message`).
- **Error Handling**: Use `tenacity` retries for all LLM API calls.
- **UI**: Use the `rich` library for terminal output formatting (Tables, Panels).

---

_Note: If you are an AI assistant helping a developer, prioritize SPADE-specific documentation over general Python threading/multiprocessing libraries._
