from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from typing import Dict, TypedDict, List, Union
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]

llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

def response(state:AgentState):
    response = llm.invoke(state['messages'])
    state['messages'].append(AIMessage(content=response.content))
    print(f'\nAI: {response.content}')
    # print(f"CURRENT STATE: {state['messages']}")
    return state

graph = StateGraph(AgentState)

graph.add_node('response', response)

graph.add_edge(START,'response')
graph.add_edge('response', END)

agent = graph.compile()

user_input=input("Enter: ")
conversational_history = []
while user_input!='exit':
    conversational_history.append(HumanMessage(content=user_input))
    result = agent.invoke({'messages':conversational_history})
    conversational_history = result['messages']
    user_input=input('Enter: ')

with open("logging.txt", "w", encoding="utf-8") as file:
    file.write("Your Conversational Log:\n")

    for message in conversational_history:
        if isinstance (message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n\n")

    file.write("End of Conversation")