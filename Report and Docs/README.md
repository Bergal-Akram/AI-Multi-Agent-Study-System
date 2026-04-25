# 🧠 Collaborative Study Intelligence System

## 📌 Overview

The **Collaborative Study Intelligence System** is an advanced Distributed Multi-Agent System (MAS) designed to automate, optimize, and evaluate academic study sessions. Developed as a Master 1 project in Artificial Intelligence and Data Science at the University of Larbi Ben M'Hidi, the system orchestrates a swarm of specialized AI agents. These agents work concurrently to generate tailored pedagogical strategies, fetch domain-specific resources, and construct interactive quizzes.

## ✨ Key Features

- **Asynchronous Agent Swarm:** Built on the SPADE framework to run multiple AI agents concurrently without blocking the main execution thread.
- **Intelligent Routing:** A central Coordinator agent dynamically routes tasks to specialized "Technical" or "Theoretical" planners based on semantic keyword analysis.
- **Anti-Bot Resource Fetching:** Staggered, domain-specific scraping for Academic papers, YouTube tutorials, and GitHub code, complete with fallback mechanisms to bypass rate limits.
- **Interactive UI Integration:** A synchronous Streamlit frontend cleanly integrated with the asynchronous SPADE backend via thread-safe UI updates and graceful event loop teardowns.
- **Session Management:** Robust Thread IDs ensure fully isolated execution, allowing multiple parallel users to query the swarm simultaneously without data crossover.

## 🏗 Architecture & Tech Stack

- **Multi-Agent Framework:** SPADE (Smart Python Agent Development Environment) over XMPP
- **Frontend & State Management:** Streamlit
- **LLM Engine:** Groq API (Llama-3.3-70b-versatile / Llama-3.1-8b-instant)
- **Concurrency:** Native Python `asyncio`

## 🛠️ Prerequisite Setup

To ensure the system runs without rate-limit conflicts, every team member must configure their own environment.

### 1. Get your Groq API Key

- Sign up at the [Groq Cloud Console](https://console.groq.com/keys).
- Generate a free **API Key**.
- _Note: Using individual keys prevents "429: Too Many Requests" errors during team testing._

### 2. Create an XMPP Account

- Register a unique Jabber ID (JID) at [xmpp.jp](https://xmpp.jp/)
- Example: `username@xmpp.jp`
- _Note: Each teammate needs a unique JID to avoid connection drops if multiple people test the system at once._

---

## 🚀 Installation & Execution

### Step 1: Clone and Environment

```bash
# Clone the repository
git clone https://github.com/Bergal-Akram/AI-Multi-Agent-Study-System.git
cd SMA_Project

# Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
pip install spade streamlit groq googlesearch-python python-dotenv tenacity

```

### step 3: Configure Environment Variables (.env)

#### The system uses environment variables for security. Never push your actual .env file to GitHub.

1. In the root folder, create a file named .env.

2. Copy the content from .env.example into .env.

3. Fill in your real credentials:

```bash
GROQ_API_KEY=gsk_your_api_key_here
USER_JID=user@your_xmpp_server
USER_PASS=your_password
COORD_JID=coord@your_xmpp_server
COORD_PASS=your_password
PLAN_TECH_JID=ptech@your_xmpp_server
PLAN_TECH_PASS=your_password
PLAN_THEORY_JID=ptheory@your_xmpp_server
PLAN_THEORY_PASS=your_password
RES_SCOUT_JID=rscout@your_xmpp_server
RES_SCOUT_PASS=your_password
RES_MEDIA_JID=rmedia@your_xmpp_server
RES_MEDIA_PASS=your_password
RES_CODE_JID=rcode@your_xmpp_server
RES_CODE_PASS=your_password
ASSESSOR_JID=quiz@your_xmpp_server
ASSESSOR_PASS=your_password
```

### Step 4: Run the System

```Bash
streamlit run main.py
```

### Project Structure

- `main.py`: Entry point. Initializes XMPP connections and starts the user proxy.
- `app/agents/`: Contains the logic for `coordinator.py`, `planner.py`, `assessor.py`, and `resourcer.py`,

- `.env.example`: Template for environment variables.

- `.gitignore`: Prevents `venv/` and `.env` from being uploaded.
