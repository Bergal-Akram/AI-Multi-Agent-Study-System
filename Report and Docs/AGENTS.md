# 🤖 Agent Architecture (AGENTS.md)

This document provides a detailed breakdown of the specialized agents within the Collaborative Study Intelligence System, explaining their roles, internal behaviors, and communication flows.

## 1. Interface Agents (The Bridge)

These agents act as proxies between the synchronous Streamlit UI and the asynchronous XMPP network.

- **UserProxy Agent (`main.py`)**:
  - **Role**: Dispatches the initial study topics to the swarm and waits for the finalized plan.
  - **Behavior**: Uses a `OneShotBehaviour` to send the payload. Crucially, it attaches a unique `session_id` to the `thread` attribute of the FIPA-ACL message, ensuring it only accepts replies belonging to the current user's session.
- **QuizProxy Agent (`main.py`)**:
  - **Role**: An ephemeral (temporary) agent spawned solely when the user clicks "Summon Quizmaster." It requests an assessment based on the active plan and safely terminates once the quiz is delivered.

## 2. Orchestration Agents (The Brain)

- **CoordinatorAgent (`coordinator.py`)**:
  - **Role**: The central router and merger of the system.
  - **Behavior**: Operates on a `CyclicBehaviour`. When a task arrives, it broadcasts the payload to _all_ specialized Planners and Resourcers concurrently using `asyncio`.
  - **Intelligent Routing**: Once all agents reply (matching the `thread_id`), it evaluates the task name. If it detects keywords like "python", "api", or "sql", it selects the Technical Planner's output. Otherwise, it selects the Theoretical Planner's output. It then consolidates all resources into a single cohesive response.

## 3. Pedagogical Agents (The Planners)

- **PlannerAgent (`planner.py`)**:
  - **Role**: Generates the 1-sentence pedagogical strategy for studying a specific topic.
  - **Expertise Variations**:
    - _Technical_: Prompted via system instructions to act as a "Senior Software Architect," focusing on practical coding and deployment strategies.
    - _Theoretical_: Prompted to act as an "Academic Professor," focusing on foundational concepts, active recall, and philosophy.
  - **Resilience**: Implements `@retry` decorators (via `tenacity`) to automatically recover from LLM rate limits.

## 4. Retrieval Agents (The Resourcers)

- **ResourcerAgent (`resourcer.py`)**:
  - **Role**: Connects the swarm to the live internet to fetch study materials.
  - **Expertise Variations**:
    - _Academic (Scout)_: Modifies Google search queries to target `site:arxiv.org` and `.edu` domains.
    - _Media (Curator)_: Targets `site:youtube.com` for visual lectures.
    - _Code (Hunter)_: Targets `site:github.com` and StackOverflow for practical examples.
  - **Anti-Bot Mechanism**: Uses `asyncio.sleep(random.uniform())` to introduce "jitter," preventing Google from blocking simultaneous requests.
  - **LLM Filtering**: Uses a strict JSON prompt with Llama-3.1-8b to select the single best link from the raw search results. Includes a robust fallback mechanism to generate direct Google Search URLs if the API fails.

## 5. Evaluation Agent (The Assessor)

- **AssessorAgent (`assessor.py`)**:
  - **Role**: The "Quizmaster." Evaluates the finalized study plan and generates a contextual multiple-choice quiz.
  - **Behavior**: Extracts topic names from the payload and enforces an extremely strict JSON schema inside the LLM prompt (mandating double quotes and specific key structures). This ensures the Streamlit UI can parse and render the interactive radio buttons without crashing.
