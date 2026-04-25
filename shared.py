import queue

# Queue to hold live messages from agents to the Streamlit UI
agent_logs = queue.Queue()

def log_message(msg):
    agent_logs.put(msg)