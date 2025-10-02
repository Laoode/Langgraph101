from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages : List[HumanMessage]

llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash")

def response(state:AgentState) -> AgentState:
    response = llm.invoke(state['messages'])
    print(f'\n AI: {response.content}')
    return state

graph = StateGraph(AgentState)
graph.add_node('response',response)

graph.add_edge(START,'response')
graph.add_edge('response',END)

agent = graph.compile()

input_user = input("Enter: ")
while input_user!='exit':
    agent.invoke({'messages':[HumanMessage(content=input_user)]})
    input_user = input("Enter: ")