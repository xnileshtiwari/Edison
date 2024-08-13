from langgraph.graph import StateGraph, END
import sys
import os
import streamlit as st
from langchain.schema import SystemMessage
from langchain_core.messages import ToolCall, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from typing import TypedDict, Annotated, List, Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
import operator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import dotenv
from tools import environment_database, final_answer, web_search 

import streamlit as st
st.page_link("Product_CO2.py", label="Home")

st.title("**Your Decisions, Our planet🌍...** Edison")

dotenv.load_dotenv()
with st.form("my_form"):
    prefilled = st.selectbox("Sample questions", ["What is the CO2 emission of iphone 14? ", "What is the CO2 emission of a Tesla Model X? ", "What is the CO2 emission of a Samsung Galaxy S22? ",])
    user_input = ""
    if st.form_submit_button("Submit"):

        with st.spinner(f'Researching {prefilled}...'):


            class AgentState(TypedDict):
                input: str
                chat_history: list[BaseMessage]
                intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


            system_prompt = """You are the oracle, the great AI decision maker.
            Given the user's query you must decide what to do with it based on the
            list of tools provided to you.

            Your main job is to calculate the CO2 emission of an item provided by the user. 
            So firstly you should search the item's brand website to see if they provide a CO2 footprint or any 
            resources that could help in calculating the CO2 emissions. 

            When you need to find information about the CO2 emission of items PLEASE prioritize
            using the environment_database. If it returns "not found" then use the search tool.

            If you see that a tool has been used (in the scratchpad) with a particular
            query, do NOT use that same tool with the same query again.

            You should aim to collect information from a diverse range of sources before
            providing the answer to the user."""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                ("assistant", "scratchpad: {scratchpad}"),
            ])

            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=os.environ["GOOGLE_API_KEY"],
                temperature=0
            )

            tools=[
                environment_database,
                web_search,
                final_answer
            ]

            system_message = SystemMessage(content=system_prompt)

            def create_scratchpad(intermediate_steps: list[AgentAction]):
                research_steps = []
                for i, action in enumerate(intermediate_steps):
                    if action.log != "TBD":
                        research_steps.append(
                            f"- Tool: {action.tool}\n  Input: {action.tool_input}\n  Output: {action.log}"
                        )
                return "\n".join(research_steps)


            # Suppress warnings
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')


            oracle = (
                {
                    "input": lambda x: x["input"],
                    "chat_history": lambda x: x["chat_history"],
                    "scratchpad": lambda x: create_scratchpad(
                        intermediate_steps=x["intermediate_steps"]
                    ),
                }

                | prompt
                | llm.bind_tools(tools, tool_choice="any")
            )
            # Restore stdout and stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__



            def run_oracle(state: list):
                out = oracle.invoke(state)
                tool_name = out.tool_calls[0]["name"]
                tool_args = out.tool_calls[0]["args"]
                action_out = AgentAction(
                    tool=tool_name,
                    tool_input=tool_args,
                    log="TBD"
                )
                return {
                    "intermediate_steps": state.get("intermediate_steps", []) + [action_out]
                } 

            def router(state: list):
                if state.get("intermediate_steps"):
                    return state["intermediate_steps"][-1].tool
                else:
                    print("Router: Starting with final_answer as no intermediate steps found.")
                    return "final_answer"

            tool_str_to_func = {
                "environment_database": environment_database,
                "web_search": web_search,
                "final_answer": final_answer
            }

            def run_tool(state: list):
                tool_name = state["intermediate_steps"][-1].tool
                tool_args = state["intermediate_steps"][-1].tool_input

                print(f"Running tool: {tool_name} with input: {tool_args}")  # Debugging line

                out = tool_str_to_func[tool_name].invoke(input=tool_args)
                action_out = AgentAction(
                    tool=tool_name,
                    tool_input=tool_args,
                    log=str(out)
                )
                # Update intermediate steps in the state
                state["intermediate_steps"].append(action_out)
                return state 

            graph = StateGraph(AgentState)
            graph.add_node("oracle", run_oracle)
            graph.add_node("environment_database", run_tool)
            graph.add_node("web_search", run_tool)
            graph.add_node("final_answer", run_tool)

            graph.set_entry_point("oracle")
            graph.add_conditional_edges(
                source="oracle", 
                path=router,  
            )

            for tool_obj in tools:
                if tool_obj.name != "final_answer":
                    graph.add_edge(tool_obj.name, "oracle")

            graph.add_edge("final_answer", END)

            runnable = graph.compile()


            initial_state = {
                "input": f"Employ any strategy you want to estimate the CO2 footprint of {prefilled}",
                "chat_history": [],
                "intermediate_steps": [] 
            }

            out = runnable.invoke(initial_state)

            def build_report(output: dict):
                research_steps = output.get("research_steps", []) 
                if isinstance(research_steps, list):
                    research_steps = "\n".join([f"- {r}" for r in research_steps])
                sources = output.get("sources", []) 
                if isinstance(sources, list):
                    sources = "\n".join([f"- {s}" for s in sources])
                return f"""
                    INTRODUCTION
                    ------------
                    {output.get("introduction", "")} 

                    RESEARCH STEPS
                    --------------
                    {research_steps}

                    REPORT
                    ------
                    {output.get("main_body", "")} 

                    CONCLUSION
                    ----------
                    {output.get("conclusion", "")} 

                    SOURCES
                    -------
                    {sources}
                    """
            



        st.success("Done!")

        # Access the final tool input from the last intermediate step
        output = (build_report(
            output=out["intermediate_steps"][-1].tool_input))

        st.write(output)

