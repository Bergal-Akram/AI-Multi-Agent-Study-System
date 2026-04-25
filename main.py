import streamlit as st
import asyncio
import json
import uuid
import os
from dotenv import load_dotenv
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

from shared import agent_logs, log_message
from app.agents.coordinator import CoordinatorAgent
from app.agents.planner import PlannerAgent
from app.agents.resourcer import ResourcerAgent
from app.agents.assessor import AssessorAgent

load_dotenv()

st.set_page_config(page_title="AI Study System", layout="wide")

# --- USER PROXY AGENT ---
# agent for user this agents act on behalf of the humain user, 
# howa li yb3ath task l coordinator w ystana full result
class UserProxy(Agent):
    def __init__(self, jid, password, task_list, session_id):
        super().__init__(jid, password)
        self.task_list = task_list
        self.session_id = session_id # this allow multi-user y3ni y9dro bzaf user ykhdmo b system sans problem, kol wahad 3ndo id w ykhdm b thread
        self.final_plan = None # to stock the result

    # oneshot behaviour run once when user yktb task ta3o
    class SendTasks(OneShotBehaviour):
        async def run(self):
            # hada message with FIPA-ACL
            msg = Message(to=os.getenv("COORD_JID")) # receiver howa COORD_JID
            msg.body = json.dumps(self.agent.task_list) # content howa task_list
            msg.thread = self.agent.session_id # hna id hadak ymdo l thread bch ykhdmo kol en parallele
            msg.set_metadata("performative", "request") # performative => request
            await self.send(msg) # hna yb3ath message
            log_message(f"[USER] Sent tasks to Coordinator (Thread: {self.agent.session_id})")

            # hadi loop infini t7bas ki yb3ath coordiantor plan for this session ID (each user)
            while True:
                resp = await self.receive(timeout=90) # wait response
                if resp and resp.thread == self.agent.session_id: # if resp is true
                    self.agent.final_plan = json.loads(resp.body) # n7ato resultat f variable final_plan
                    log_message("[USER] Received final multi-agent plan!")
                    break

    async def setup(self):
        self.add_behaviour(self.SendTasks())

# --- ASYNC EXECUTION WRAPPERS ---
async def run_study_generation(tasks, session_id):
    # Streamlit cannot natively run async functions, so we wrap the SPADE 
    # agent lifecycle in these functions and manage the asyncio event loop manually.
    
    # hna ndiro initialisation t3 les agents li 3ndna avec expertise and resource type
    c = CoordinatorAgent(os.getenv("COORD_JID"), os.getenv("COORD_PASS"))
    p_tech = PlannerAgent(os.getenv("PLAN_TECH_JID"), os.getenv("PLAN_TECH_PASS"), expertise="technical")
    p_theory = PlannerAgent(os.getenv("PLAN_THEORY_JID"), os.getenv("PLAN_THEORY_PASS"), expertise="theoretical")
    r_scout = ResourcerAgent(os.getenv("RES_SCOUT_JID"), os.getenv("RES_SCOUT_PASS"), resource_type="academic")
    r_media = ResourcerAgent(os.getenv("RES_MEDIA_JID"), os.getenv("RES_MEDIA_PASS"), resource_type="media")
    r_code = ResourcerAgent(os.getenv("RES_CODE_JID"), os.getenv("RES_CODE_PASS"), resource_type="code")
    
    agents = [c, p_tech, p_theory, r_scout, r_media, r_code]
    for agent in agents:
        await agent.start() # connect all agent to the XMPP server
    
    user = UserProxy(os.getenv("USER_JID"), os.getenv("USER_PASS"), tasks, session_id)
    await user.start() # run user agent 
    
    # Wait until the UserProxy receives the final plan
    while user.final_plan is None:
        await asyncio.sleep(0.5)
        
    # hna ki yb3ath final plan y liberer les agents for other users
    for agent in agents + [user]:
        await agent.stop()
        
    return user.final_plan # return final plan

async def run_quiz_generation(plan_data, session_id):
    a = AssessorAgent(os.getenv("ASSESSOR_JID"), os.getenv("ASSESSOR_PASS"))
    await a.start() # run quiz agent (assessor agent it generate Quiz based on the plan that it generate from planner agent)
    
    class QuizProxy(Agent):
        def __init__(self, jid, passw):
            super().__init__(jid, passw)
            self.quiz = None # to stock the result
        # oneshot behaviour run once when user 7ab l'QUIZ
        class AskQuiz(OneShotBehaviour):
            async def run(self):
                # msg with FIPA-ACL
                msg = Message(to=os.getenv("ASSESSOR_JID")) # receiver is ASSESSOR
                msg.body = json.dumps(plan_data) # content is Plan data
                msg.thread = session_id # initial a thread for this session
                await self.send(msg) # send the msg
                log_message("[USER] send plan data to generate QUIZ")
                # boucle infini until resp receiver
                while True:
                    resp = await self.receive(timeout=60) # wait resp
                    if resp and resp.thread == session_id:
                        self.agent.quiz = json.loads(resp.body) # stock result in quiz variable
                        break # break its mean stop the boucle when resp receiver
        async def setup(self): 
            self.add_behaviour(self.AskQuiz())
 
    qp = QuizProxy(os.getenv("USER_JID"), os.getenv("USER_PASS"))
    await qp.start() # start agent user 
    while qp.quiz is None:
        await asyncio.sleep(0.5) # wait until quiz receiver from agent
    await qp.stop(); # stop user agent 
    await a.stop() # stop assesor agent bc it finished his work
    return qp.quiz # return result

# --- UI DESIGN ---
# Title and description of the app
st.title("Collaborative Study Intelligence System")
st.markdown("Distributed Multi-Agent Architecture")

# Create two tabs: one for plan generation, one for quiz
tab_plan, tab_quiz = st.tabs(["Study Plan Generator", "Quizmaster Assessor"])


# =========================
# TAB 1: STUDY PLAN
# =========================
with tab_plan:

    # Form for user input
    with st.form("task_form"):

        # Create 3 columns for structured input
        col_t, col_time, col_d = st.columns(3)

        # Input fields
        task_name = col_t.text_input("Task Topic", "Linear regression Machine Learning")
        time_alloc = col_time.text_input("Time Allocation", "2 Hours")
        deadline = col_d.date_input("Deadline")

        # Submit button
        submitted = st.form_submit_button("Orchestrate AI Agents")

    # -----------------------------------------
    # 1) EXECUTE ONLY WHEN BUTTON IS CLICKED
    # -----------------------------------------
    if submitted:

        # Create unique session ID (used to track agent communication)
        session_id = str(uuid.uuid4())[:8]

        # Prepare task structure
        tasks = [{
            "name": task_name,
            "time": time_alloc,
            "deadline": str(deadline)
        }]

        # Split UI into main content + logs panel
        col_main, col_logs = st.columns([2, 1])

        # Logs section (right side)
        with col_logs:
            st.markdown("### 📡 Agent Logs")
            log_container = st.empty()  # Placeholder to update logs dynamically

        # Main execution area
        with col_main:
            with st.spinner("Initializing Agent Swarm..."):

                # Create a new asyncio event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Launch async multi-agent task
                task = loop.create_task(
                    run_study_generation(tasks, session_id)
                )

                logs = ""

                # While agents are running → update logs in real-time
                while not task.done():

                    # Let event loop run briefly
                    loop.run_until_complete(asyncio.sleep(0.5))

                    # Pull logs from shared queue
                    while not agent_logs.empty():
                        logs += f"**> {agent_logs.get()}**\n\n"
                        log_container.info(logs)

                # Save results in session state (persists across reruns)
                st.session_state['current_plan'] = task.result()
                st.session_state['session_id'] = session_id

                # -----------------------------------------
                # CLEAN ASYNCIO LOOP (VERY IMPORTANT)
                # -----------------------------------------
                pending = asyncio.all_tasks(loop)

                for t in pending:
                    t.cancel()  # Cancel background tasks (e.g., SPADE XMPP)

                # Give tasks time to shutdown
                loop.run_until_complete(asyncio.sleep(0.1))

                # Close loop to avoid Streamlit errors
                loop.close()


    # -----------------------------------------
    # 2) ALWAYS DISPLAY PLAN IF IT EXISTS
    # -----------------------------------------
    if 'current_plan' in st.session_state:

        st.success("Study Plan is active!")

        # Display each task
        for item in st.session_state['current_plan']:

            # Task title and metadata
            st.markdown(
                f"### {item['name']} "
                f"(Due: {item['deadline']} | {item['time']})"
            )

            # AI-generated study method
            st.info(f"**AI Strategy:** {item['method']}")

            # Resources section
            st.markdown("**Resources:**")

            for r in item.get('resources', []):
                st.markdown(
                    f"- [{r['type'].upper()}] "
                    f"[{r['name']}]({r['url']})"
                )


# =========================
# TAB 2: QUIZ
# =========================
with tab_quiz:

    st.markdown("### Test Your Knowledge")

    # If no plan exists → block quiz generation
    if 'current_plan' not in st.session_state:
        st.warning("Please generate a study plan first!")

    else:
        # Button to trigger quiz generation
        if st.button("Summon Quizmaster Agent"):

            with st.spinner("Quizmaster is analyzing your study plan..."):

                # Create new asyncio loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Run quiz generation (async → sync)
                quiz = loop.run_until_complete(
                    run_quiz_generation(
                        st.session_state['current_plan'],
                        st.session_state['session_id']
                    )
                )

                # Save quiz in session state
                st.session_state['current_quiz'] = quiz

                # -----------------------------------------
                # CLEAN ASYNCIO LOOP
                # -----------------------------------------
                pending = asyncio.all_tasks(loop)

                for t in pending:
                    t.cancel()

                loop.run_until_complete(asyncio.sleep(0.1))
                loop.close()


        # -----------------------------------------
        # ALWAYS DISPLAY QUIZ IF IT EXISTS
        # -----------------------------------------
        if 'current_quiz' in st.session_state:

            st.success("Quiz Generated!")

            for i, q in enumerate(st.session_state['current_quiz']):

                # Display question
                st.markdown(f"**Q{i+1}: {q['question']}**")

                # Radio buttons for answers
                st.radio(
                    "Options:",
                    q['options'],
                    key=f"q_{i}"  # unique key required by Streamlit
                )

                # Reveal answer (hidden by default)
                with st.expander("Reveal Answer"):
                    st.success(q['answer'])