import json
import os
import re
from dotenv import load_dotenv
from groq import Groq
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from googlesearch import search
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
print(f"DEBUG: API Key found: {os.getenv('GROQ_API_KEY')[:10]}...")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ResourcerAgent(Agent):
    class ResourceBehaviour(CyclicBehaviour):
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=6))
        def clean_with_ai(self, search_data, topic):
            prompt = f"Pick the 2 best educational links for '{topic}' from: {search_data}. Return ONLY JSON: [{{'name': 'Title', 'url': '...'}}]"
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.1,
            )
            return chat_completion.choices[0].message.content

        async def run(self):
            msg = await self.receive(timeout=30)
            if msg and msg.body:
                print("[RESOURCER] Searching Web + AI Verification...")
                tasks = json.loads(msg.body)
                for task in tasks:
                    try:
                        query = f"{task['name']} tutorial documentation"
                        raw_links = [url for url in search(query, num_results=4)]
                        ai_response = self.clean_with_ai(raw_links, task['name'])
                        match = re.search(r'\[.*\]', ai_response, re.DOTALL)
                        task["resources"] = json.loads(match.group()) if match else [{"name": "Documentation", "url": raw_links[0]}]
                    except Exception:
                        task["resources"] = [{"name": "Search Link", "url": f"https://google.com/search?q={task['name']}"}]

                reply = Message(to=str(msg.sender))
                reply.body = json.dumps(tasks)
                reply.set_metadata("performative", "inform")
                await self.send(reply)

    async def setup(self):
        self.add_behaviour(self.ResourceBehaviour())