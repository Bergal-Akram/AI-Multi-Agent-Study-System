import json
import os
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from dotenv import load_dotenv

load_dotenv()
print(f"DEBUG: API Key found: {os.getenv('GROQ_API_KEY')[:10]}...")

class CoordinatorAgent(Agent):
    class CoordinatorBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=60)
            if msg and msg.get_metadata("performative") == "request":
                print("[COORDINATOR] Orchestrating Agents...")
                
                # Fetch JIDs from environment
                planner_jid = os.getenv("planner_USER1")
                resource_jid = os.getenv("resource_USER2")

                for jid in [planner_jid, resource_jid]:
                    out_msg = Message(to=jid)
                    out_msg.body = msg.body
                    out_msg.set_metadata("performative", "query")
                    await self.send(out_msg)

                planner_data, resource_data = None, None

                while planner_data is None or resource_data is None:
                    incoming = await self.receive(timeout=30)
                    if incoming:
                        if planner_jid in str(incoming.sender):
                            planner_data = json.loads(incoming.body)
                        elif resource_jid in str(incoming.sender):
                            resource_data = json.loads(incoming.body)

                for i in range(len(planner_data)):
                    planner_data[i]["resources"] = resource_data[i].get("resources", [])

                reply = Message(to=str(msg.sender))
                reply.body = json.dumps(planner_data)
                await self.send(reply)
                print("[COORDINATOR] Final plan merged and sent.")

    async def setup(self):
        self.add_behaviour(self.CoordinatorBehaviour())