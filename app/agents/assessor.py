# Standard libraries
import json
import os
import re

# Load environment variables (.env)
from dotenv import load_dotenv 

# Groq LLM client
from groq import Groq

# SPADE multi-agent framework
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

# Custom logging utility
from shared import log_message


# Load environment variables (e.g., GROQ_API_KEY)
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class AssessorAgent(Agent):
    """
    Agent responsible for generating quizzes based on a study plan.
    """

    class AssessorBehaviour(CyclicBehaviour):
        """
        Behaviour that:
        - receives study plan
        - generates quiz using LLM
        - returns structured JSON quiz
        """

        async def run(self):
            """
            Main loop:
            - Waits for incoming study plan
            - Generates quiz
            - Sends it back
            """

            # Wait for message (timeout = 30 seconds)
            msg = await self.receive(timeout=30)

            if msg:
                # Log activity
                log_message("[QUIZMASTER] Generating test based on study plan...")

                # Parse incoming JSON (study plan)
                plan_data = json.loads(msg.body)

                # Extract only topic names
                topics = [t['name'] for t in plan_data]

                # Strict prompt to force valid JSON output
                prompt = f"""
Create a 3-question multiple choice quiz testing these topics: {topics}.
Return ONLY valid JSON. You MUST use double quotes for all keys and strings.
Format exactly like this:
[
  {{"question": "What is...", "options": ["A", "B", "C"], "answer": "Exact match of correct option"}}
]
"""

                try:
                    # Call Groq LLM
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",

                        # Low temperature → more deterministic & structured output
                        temperature=0.2,
                    )

                    # Raw model response (may contain extra text)
                    response_text = chat.choices[0].message.content

                    # Extract JSON array using regex
                    match = re.search(r'\[.*\]', response_text, re.DOTALL)

                    if match:
                        # Convert extracted JSON string into Python object
                        quiz = json.loads(match.group())
                    else:
                        # If no JSON detected → force error handling
                        raise ValueError("No JSON array found in LLM response.")

                except Exception as e:
                    # Log parsing/API error
                    log_message(f"[QUIZMASTER] Error parsing JSON: {str(e)[:50]}")

                    # Fallback quiz (prevents system crash)
                    quiz = [{
                        "question": "JSON Parsing Failed. Try again.",
                        "options": ["A"],
                        "answer": "A"
                    }]

                # Prepare reply message
                reply = Message(to=str(msg.sender))

                # Convert quiz to JSON string
                reply.body = json.dumps(quiz)

                # Preserve thread context
                reply.thread = msg.thread

                # Send response
                await self.send(reply)


    async def setup(self):
        """
        Called when agent starts.
        Registers behaviour.
        """
        self.add_behaviour(self.AssessorBehaviour())