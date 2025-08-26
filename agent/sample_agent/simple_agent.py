"""
Simple agent for testing CopilotKit-LangGraph integration.
"""

from typing_extensions import Literal, TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from copilotkit import CopilotKitState

class SimpleAgentState(CopilotKitState):
    """Simple state for testing."""
    pass

async def simple_chat_node(state: SimpleAgentState, config) -> Command[Literal["__end__"]]:
    """Simple chat node that just echoes back the message."""
    messages = state.get("messages", [])
    
    # Get the last user message
    last_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_message = msg
            break
    
    if last_message:
        # Create a simple response
        response = AIMessage(content=f"Hello! You said: {last_message.content}")
        updated_messages = messages + [response]
    else:
        response = AIMessage(content="Hello! I'm a simple test agent.")
        updated_messages = messages + [response]
    
    return Command(
        goto=END,
        update={"messages": updated_messages},
    )

# Create the workflow
workflow = StateGraph(SimpleAgentState)
workflow.add_node("chat_node", simple_chat_node)
workflow.set_entry_point("chat_node")

# Compile the workflow
simple_graph = workflow.compile(MemorySaver())
