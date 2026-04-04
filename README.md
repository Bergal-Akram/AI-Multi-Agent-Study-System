# 🎓 AI Multi-Agent Study System (SMA)

This project is a Distributed Multi-Agent System (MAS) designed to automate the creation of personalized study plans. Built with **SPADE** and **Python**, it demonstrates how independent agents can collaborate using the **XMPP protocol** to provide high-reasoning strategies and live web resources.

---

## 🏗️ System Architecture

The system follows a "Coordinator-Worker" pattern where tasks are delegated to specialized AI agents:

- **Coordinator Agent**: The entry point. It manages the lifecycle of the other agents, handles user input, and assembles the final study plan into a formatted UI table.
- **Planner Agent**: The "Strategist." Powered by **Llama-3.3-70B**, it calculates time distribution and pedagogical methods based on the user's deadline.
- **Resourcer Agent**: The "Researcher." A hybrid agent that uses **Google Search tools** to find live links and **Llama-3.1-8B** to verify and format them into clean JSON data.

---

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

```

### step 3: Configure Environment Variables (.env)

#### The system uses environment variables for security. Never push your actual .env file to GitHub.

1. In the root folder, create a file named .env.

2. Copy the content from .env.example into .env.

3. Fill in your real credentials:

```bash
GROQ_API_KEY=gsk_your_real_key_here
Coordinator_USER=example@xmpp.jp
Coordinator_PASS=your_password

planner_USER1=example@xmpp.jp
planner_PASS1=your_password

resource_USER2=example@xmpp.jp
resource_PASS2=your_password

XMPP_USER3=example@xmpp.jp
XMPP_PASS3=your_password
```

### Step 4: Run the System

```Bash
python main.py
```

### Project Structure

- `main.py`: Entry point. Initializes XMPP connections and starts the user proxy.
- `app/agents/`: Contains the logic for `coordinator.py`, `planner.py`, and `resourcer.py`.

- `.env.example`: Template for environment variables.

- `.gitignore`: Prevents `venv/` and `.env` from being uploaded.
