from typing import TypedDict, List, Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv 

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

#global variable to store document
document_content = ""

@tool
def update(content:str)->str:
    """Updates the document with the provided content."""
    global document_content
    document_content=content
    return f"Your document has been updated succesfully! The current document is:\n{document_content}"

@tool
def save(filename:str)->str:
    """Save the current document to a text file and finish the process.
    
    Args:
        filename: name for the text file
    """
    global document_content
    if not document_content:
        return "Error: Document is empty. Please update the document first before saving."
    
    if not filename.endswith(".txt"):
        filename=f"{filename}.txt"
    try:
        with open (filename, "w", encoding="utf-8") as file:
            file.write(document_content)
        print(f"\n 💾 Document has been saved to: '{filename}'")
        return f"Your document has been saved succesfully to '{filename}'"
    except Exception as e:
        return f"Error saving document: {str(e)}"

tools = [update, save]
llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash").bind_tools(tools)

def agent(state: AgentState)->AgentState:
    global document_content
    system_prompt=SystemMessage(content = f"""
    Your Drafter Agent, a helpfull writing assistant. You're going to help a user to update and modify documents.

    - If the user wants to create or update or modifying content, you're using 'update' tool with the complate updated content.
    - If the user wants to save and finish, you need to 'save' tool (only after content is updated).
    - Make sure to always show the current document state after modifications.
    - The document must have content before it can be saved.

    The curent document content is: {document_content}
    """)
    
    if not state["messages"]:
        user_input = "I'm ready to help you update a document. What whould you like to create?"
        user_message = HumanMessage(content=user_input)
    else:
        user_input=input("\nWhat whould you like to do with the document? ")
        print(f"\n 👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)
    
    all_message = [system_prompt] + list(state["messages"]) + [user_message]
    response = llm.invoke(all_message)

    print(f"\n🤖AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🔧 USING TOOLS: {tc['name'] for tc in response.tool_calls}")

    return {"messages":list(state["messages"]) + [user_message, response]}

def should_continue(state:AgentState)->str:
    
    messages = state["messages"]
    if not messages:
        return "continue"
    
    for message in reversed(messages):

        if (isinstance(message, ToolMessage) and
            "saved" in message.content.lower() and
            "document" in message.content.lower()):
            return "exit"
        
    return "continue"

def print_message(messages):
    if not messages:
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n🧰 TOOL RESULT: {message.content}")

graph = StateGraph(AgentState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue":"agent",
        "exit": END
    }
)

app = graph.compile()

def run_document_agent():
    print("\n======DRAFTER======")

    state = {"messages": []}
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_message(step["messages"])

    print("\n======DRAFTER FINISHED======")

if __name__ == "__main__":
    run_document_agent()