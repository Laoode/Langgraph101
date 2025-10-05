from typing import TypedDict, List, Annotated, Sequence
from operator import add as add_messages
import os
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()
pdf_path = "The_Stock_Market_Story_2025.pdf"
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found: {pdf_path}")

pdf_loader = PyPDFLoader(pdf_path)

try:
    pages= pdf_loader.load()
    print(f"PDF has been loaded and has {len(pages)} pages.")
except Exception as e:
    print(f"Error loading PDF: {e}")
    raise


# chunking process
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

pages_split = text_splitter.split_documents(pages)

# this for chroma database directory
persist_directory = r"D:\Documents\COURSE\LangGraph\AIAgents"
collection_name = "stock_market"
# if not exist create a new one
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)

try:
    # create the chroma database using embeddings model
    vector_store = Chroma.from_documents(
        documents = pages_split,
        embedding = embeddings,
        persist_directory = persist_directory,
        collection_name = collection_name
    )
    print("Create ChromaDB vector store!")
except Exception as e:
    print(f"Error setting up ChromaDB: {e}")
    raise

# Now, create retriever
retriever  = vector_store.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k":5} # k is the amount of chunks to return
)

@tool
def retriever_tool(query: str)->str:
    """
    This tool searches and return the information from Stock Market Performance Story 2025 document. 
    """
    docs = retriever.invoke(query)
    if not docs:
        return "I found no relevant information in the stock market performance story 2025 document."
    
    results = []

    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}:\n{doc.page_content}")

    return "\n\n".join(results)

tools = [retriever_tool]
llm = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def should_continue(state: AgentState):
    """Check if the last message contain tool cals"""
    result = state["messages"][-1]
    return hasattr(result, 'tool_calls') and len(result.tool_calls)>0

system_prompt = """
You are an intelligent AI assistant who answers questions about Stock Market Performance Story in 2025 based on the PDF document loaded into your knowledge base.
Use the retriever tool available to answer questions about the stock market performance data. You can make multiple calls if needed.
If you need to look up some information before asking a follow up question, you are allowed to do that!
Please always cite the specific parts of the documents you use in your answers.
"""

tools_dict = {our_tool.name: our_tool for our_tool in tools} # Creating a dictionary of our tools

# LLM Agent
def call_llm(state: AgentState) -> AgentState:
    """Function to call the LLM with the current state."""
    messages = list(state['messages'])
    messages = [SystemMessage(content=system_prompt)] + messages
    message = llm.invoke(messages)
    return {'messages': [message]}


# Retriever Agent
def take_action(state: AgentState) -> AgentState:
    """Execute tool calls from the LLM's response."""

    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:
        print(f"Calling Tool: {t['name']} with query: {t['args'].get('query', 'No query provided')}")
        
        if not t['name'] in tools_dict: # Checks if a valid tool is present
            print(f"\nTool: {t['name']} does not exist.")
            result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."
        
        else:
            result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
            print(f"Result length: {len(str(result))}")      

        # Appends the Tool Message
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tools Execution Complete. Back to the model!")
    return {'messages': results}

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("retriever",take_action)

graph.set_entry_point("llm")

graph.add_conditional_edges(
    "llm",
    should_continue,
    {
        True: "retriever",
        False: END 
    }
)
graph.add_edge("retriever", "llm")
rag_agent = graph.compile()

def running_agent():
    print("\n=== RAG AGENT===")
    
    while True:
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        messages = [HumanMessage(content=user_input)] # converts back to a HumanMessage type

        result = rag_agent.invoke({"messages": messages})
        
        print("\n=== ANSWER ===")
        print(result['messages'][-1].content)


running_agent()