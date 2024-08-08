from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
import os
from typing import Annotated, Literal, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from tools import calculator, pollution, search, tool
load_dotenv()  





tool = [search, pollution, calculator]




tool_node = ToolNode(tool)
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0).bind_tools(tool)






# Define the function that determines whether to continue or not
def should_continue(state: MessagesState) -> Literal["tools", END]:  # type: ignore
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, we stop (reply to the user)
    return END




# Define the function that calls the model
def call_model(state: MessagesState):
    messages = state['messages']
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}




# Define a new graph
workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", 'agent')

checkpointer = MemorySaver()

app = workflow.compile(checkpointer=checkpointer)






# Use the Runnable
final_state = app.invoke(
    {"messages": [HumanMessage(content="2 add 2")]},
    config={"configurable": {"thread_id": 42}}
)
final_state["messages"][-1].content





print(final_state["messages"][-1].content)
