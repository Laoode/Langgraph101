from typing import Dict, TypedDict, Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a:int, b:int):
    """This is addition function that adds 2 numbers together"""
    return a+b

@tool
def subtract(a: int, b: int):
    """Subtraction function"""
    return a-b

@tool
def multiply(a: int, b:int):
    """Multiplication function"""
    return a*b

tools = [add, subtract, multiply]

llm = ChatGoogleGenerativeAI(model= "gemini-2.0-flash").bind_tools(tools)

def model_call(state: AgentState)-> AgentState:
    system_prompt = SystemMessage(content="Your my AI asisten, please answer my question to the best of your ability")
    response = llm.invoke([system_prompt] + state['messages'])

    return {"messages":[response]}

def should_continue(state:AgentState)->str:
    messages = state['messages']
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "exit"
    else:
        return "continue"

graph = StateGraph(AgentState)
graph.add_node('our_agent', model_call)

tools = ToolNode(tools=tools)
graph.add_node('tools', tools)

graph.set_entry_point('our_agent')
#one way directed edge
graph.add_conditional_edges( 
    'our_agent',
    should_continue,
    {
        'continue':'tools',
        'exit':END
    }
)
#this node back to the agent
graph.add_edge('tools','our_agent')

agent = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s['messages'][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs= {"messages": [("user", "Add 3+7, and the result adding again with 90, and then the result substract with the result of first add operation before, and the result again multiply with 2. And also tell me a joke")]}
print_stream(agent.stream(inputs, stream_mode="values"))