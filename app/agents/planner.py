import json
import os
from dotenv import load_dotenv
from groq import Groq
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
print(f"DEBUG: API Key found: {os.getenv('GROQ_API_KEY')[:10]}...")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class PlannerAgent(Agent):
    class PlannerBehaviour(CyclicBehaviour):
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=6))
        def call_groq(self, prompt):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
            )
            return chat_completion.choices[0].message.content

        async def run(self):
            msg = await self.receive(timeout=30)
            if msg and msg.body:
                print("[PLANNER] Llama-3 (Groq) is drafting strategies...")
                tasks = json.loads(msg.body)
                for task in tasks:
                    try:
                        prompt = f"Give a specific 1-sentence study technique for {task['name']} for a {task['time']} session."
                        response = self.call_groq(prompt)
                        task["method"] = response.strip()
                    except Exception as e:
                        task["method"] = f"Review {task['name']} documentation."

                reply = Message(to=str(msg.sender))
                reply.body = json.dumps(tasks)
                reply.set_metadata("performative", "inform")
                await self.send(reply)

    async def setup(self):
        self.add_behaviour(self.PlannerBehaviour())