import json
import os
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from shared import log_message

class CoordinatorAgent(Agent):
    # CyclicBehaviour means the agent stays alive and continuously listens for incoming messages
    class CoordinatorBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=60) # wait until msg receive 
            if msg and msg.get_metadata("performative") == "request": # check 
                thread_id = msg.thread # extract the unique session ID
                log_message(f"[COORDINATOR] Orchestrating task swarm for Thread {thread_id}...")
                
                # define who the target to send
                target_jids = [
                    os.getenv("PLAN_TECH_JID"), os.getenv("PLAN_THEORY_JID"),
                    os.getenv("RES_SCOUT_JID"), os.getenv("RES_MEDIA_JID"), os.getenv("RES_CODE_JID")
                ]

                # Broadcast to all specialized agents (in spade we define broadcast performative as a loop) not like we studyy
                for jid in target_jids:
                    out = Message(to=jid) # to all agent in target
                    out.body = msg.body # content is the msg body, means task input
                    out.thread = thread_id # each one have thread to work parallele
                    out.set_metadata("performative", "query") # with performative Query
                    await self.send(out) # here we send 

                # ASYNC COLLECTION: Create a dictionary to hold the results as they arrive in unpredictable order
                results = {"tech": None, "theory": None, "academic": None, "media": None, "code": None}
                
                # Wait until every specialized agent has replied for THIS specific thread
                while None in results.values():
                    incoming = await self.receive(timeout=10) # wait response
                    if incoming and incoming.thread == thread_id and incoming.body:
                        try:
                            # Safely attempt to parse the incoming message to avoid crashing on XMPP server MOTD messages
                            incoming_data = json.loads(incoming.body) # load response into incoming_data variable
                        except json.JSONDecodeError:
                            continue # Skip bad messages and keep waiting, Safely attempt to parse the incoming message to avoid crashing on XMPP server MOTD messages
                        
                        # Map the incoming data to the correct slot based on the sender's JID
                        sender = str(incoming.sender)
                        if os.getenv("PLAN_TECH_JID") in sender: results["tech"] = incoming_data
                        elif os.getenv("PLAN_THEORY_JID") in sender: results["theory"] = incoming_data
                        elif os.getenv("RES_SCOUT_JID") in sender: results["academic"] = incoming_data
                        elif os.getenv("RES_MEDIA_JID") in sender: results["media"] = incoming_data
                        elif os.getenv("RES_CODE_JID") in sender: results["code"] = incoming_data

                log_message(f"[COORDINATOR] All agents reported. Merging plan for Thread {thread_id}.")
                final_plan = self.merge_logic(json.loads(msg.body), results) # final plan in final_plan after merge logic

                reply = Message(to=str(msg.sender)) # reply to the sender
                reply.body = json.dumps(final_plan) # content have final plan
                reply.thread = thread_id # initiale a thread
                await self.send(reply) # send reply

        def merge_logic(self, tasks, results):
            """
            Intelligent Routing System: Evaluates the topic of the task to determine
            whether the Technical or Theoretical planner provided the better strategy.
            """
            final = []
            for i in range(len(tasks)):
                task = tasks[i]
                name = task['name'].lower()
                
                # Keyword-based heuristics to select the appropriate pedagogical method
                if any(k in name for k in ["python", "ai", "data", "code", "sql", "api", "spring"]):
                    task["method"] = results["tech"][i]["method"]
                else:
                    task["method"] = results["theory"][i]["method"]
                    
                # Combine all resource types
                task["resources"] = []
                for r_type in ["academic", "media", "code"]:
                    task["resources"].extend(results[r_type][i].get("resources", []))
                
                final.append(task)
            return final

    async def setup(self):
        self.add_behaviour(self.CoordinatorBehaviour())