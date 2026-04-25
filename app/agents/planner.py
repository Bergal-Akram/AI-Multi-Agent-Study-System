import json
import os
from dotenv import load_dotenv
from groq import Groq
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from tenacity import retry, stop_after_attempt, wait_exponential
from shared import log_message

load_dotenv() 
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class PlannerAgent(Agent):
    def __init__(self, jid, password, expertise):
        super().__init__(jid, password)
        self.expertise = expertise # Defines the agent's persona ('technical' or 'theoretical')

    class PlannerBehaviour(CyclicBehaviour):
        # Apply retry logic to the function
        @retry(
            stop=stop_after_attempt(3),  # Stop after 3 failed attempts
            wait=wait_exponential(
                multiplier=1,  # Base multiplier for exponential backoff
                min=2,         # Minimum wait time between retries (seconds)
                max=6          # Maximum wait time between retries (seconds)
            )
        )
        # this function we call it when we need the model to generate our plan
        def call_groq(self, prompt, role_sys):
            """
            Sends a chat request to the Groq API and returns the model's response.

            Parameters:
            - prompt (str): The user's input message
            - role_sys (str): System instruction that defines model behavior

            Returns:
            - str: The generated response from the model
            """

            # Create a chat completion request to the Groq API
            chat = client.chat.completions.create(
                messages=[
                    # System message: controls how the model should behave
                    {"role": "system", "content": role_sys},

                    # User message: actual input/question
                    {"role": "user", "content": prompt}
                ],

                # Specify the model to use
                model="llama-3.3-70b-versatile",

                # Controls randomness (0 = deterministic, 1 = very random)
                temperature=0.4  # Balanced for logical and structured responses
            )

            # Extract and return only the generated text from the response
            return chat.choices[0].message.content

        async def run(self):
            """
            Main loop executed repeatedly:
            - Waits for incoming messages
            - Processes tasks
            - Sends back enriched results
            """

            # Wait for a message (timeout after 30 seconds)
            msg = await self.receive(timeout=30)

            # Ensure message exists and has content
            if msg and msg.body:
                try:
                    # Parse JSON message body into Python object
                    tasks = json.loads(msg.body)

                except json.JSONDecodeError:
                    # Ignore invalid/non-JSON messages (e.g., system noise)
                    return

                # Log activity (for UI interface) to show it in interface communication
                log_message(
                    f"[PLANNER-{self.agent.expertise.upper()}] Drafting strategy..."
                )

                # Define system role based on agent expertise
                if self.agent.expertise == "technical":
                    role_sys = "You are a Senior Software Architect and Data Scientist."
                else:
                    role_sys = "You are an Academic Professor specializing in philosophy and deep theoretical concepts."

                # Process each task
                for task in tasks:
                    try:
                        # Build prompt dynamically
                        prompt = (
                            f"Give a specific 1-sentence study technique "
                            f"for '{task['name']}' for a {task['time']} session."
                        )

                        # Call LLM and attach result to task
                        task["method"] = self.call_groq(prompt, role_sys).strip()

                    except Exception:
                        # Fallback in case of API failure
                        task["method"] = "Review documentation."

                # Create reply message
                reply = Message(to=str(msg.sender))

                # Convert updated tasks back to JSON
                reply.body = json.dumps(tasks)

                # Preserve conversation thread
                reply.thread = msg.thread

                # Send response back to sender
                await self.send(reply)


    async def setup(self):
        """
        Called when the agent starts.
        Registers its behaviour.
        """
        self.add_behaviour(self.PlannerBehaviour())