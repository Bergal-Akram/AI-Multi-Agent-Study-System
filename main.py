import asyncio
import json
import os
from dotenv import load_dotenv
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from app.agents.coordinator import CoordinatorAgent
from app.agents.planner import PlannerAgent
from app.agents.resourcer import ResourcerAgent

load_dotenv()
print(f"DEBUG: API Key found: {os.getenv('GROQ_API_KEY')[:10]}...")
console = Console()

class UserProxy(Agent):
    def __init__(self, jid, password, task_list):
        super().__init__(jid, password)
        self.task_list = task_list

    class SendTasks(OneShotBehaviour):
        async def run(self):
            # Target the Coordinator from .env
            msg = Message(to=os.getenv("Coordinator_USER"))
            msg.body = json.dumps(self.agent.task_list)
            msg.set_metadata("performative", "request")
            await self.send(msg)
            
            console.print("\n[bold yellow]AI Brainstorming in progress...[/bold yellow]")
            resp = await self.receive(timeout=90)
            
            if resp and resp.body:
                final_data = json.loads(resp.body)
                table = Table(title="AI GENERATED STUDY PLAN", show_lines=True)
                table.add_column("Task", style="bold cyan")
                table.add_column("AI Strategy & Deadline", style="white", width=60)
                table.add_column("Resources", style="green", overflow="fold")

                for item in final_data:
                    res_str = "\n".join([f"• {r['name']}: {r['url']}" for r in item.get('resources', [])])
                    table.add_row(item['name'], f"{item.get('method')}\n\nTime: {item['time']} | Due: {item['deadline']}", res_str)
                console.print(table)

    async def setup(self):
        self.add_behaviour(self.SendTasks())

async def main():
    # Load Credentials from .env
    c_jid, c_pw = os.getenv("Coordinator_USER"), os.getenv("Coordinator_PASS")
    p_jid, p_pw = os.getenv("planner_USER1"), os.getenv("planner_PASS1")
    r_jid, r_pw = os.getenv("resource_USER2"), os.getenv("resource_PASS2")
    u_jid, u_pw = os.getenv("XMPP_USER3"), os.getenv("XMPP_PASS3")

    p = PlannerAgent(p_jid, p_pw); r = ResourcerAgent(r_jid, r_pw); c = CoordinatorAgent(c_jid, c_pw)
    await p.start(); await r.start(); await c.start()
    await asyncio.sleep(2)

    console.print(Panel("[bold magenta]AI MULTI-AGENT STUDY SYSTEM[/bold magenta]"))
    num = int(console.input("[bold]How many tasks? [/bold]"))
    tasks = [{"name": console.input(f"T{i+1} Name: "), "time": console.input("Time: "), "deadline": console.input("Deadline: ")} for i in range(num)]

    user = UserProxy(u_jid, u_pw, tasks)
    await user.start()
    while user.is_alive(): await asyncio.sleep(1)
    await user.stop(); await p.stop(); await r.stop(); await c.stop()

if __name__ == "__main__":
    asyncio.run(main())