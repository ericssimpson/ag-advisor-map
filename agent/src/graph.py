from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from typing import TypedDict, Annotated
import operator

# Assume these functions exist to interact with Instabase
from instabase_api import extract_document_data, process_workflow

# Define the state
class State(TypedDict):
    messages: Annotated[list[str], operator.add]
    document_data: dict
    processed_result: dict

# Create tools
tools = [
    Tool(name="extract_data", func=extract_document_data, description="Extract data from a document using Instabase"),
    Tool(name="process_workflow", func=process_workflow, description="Run an Instabase workflow on extracted data")
]

# Create LLM
llm = ChatOpenAI()

# Define graph nodes
def extract_document_node(state):
    document_id = state["messages"][-1]  # Assume last message is document ID
    data = extract_document_data(document_id)
    return {"document_data": data}

def process_data_node(state):
    result = process_workflow(state["document_data"])
    return {"processed_result": result}

def analyze_result_node(state):
    prompt = f"Analyze this result: {state['processed_result']}"
    response = llm.predict(prompt)
    return {"messages": [response]}

# Create graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("extract_document", extract_document_node)
workflow.add_node("process_data", process_data_node)
workflow.add_node("analyze_result", analyze_result_node)

# Define edges
workflow.set_entry_point("extract_document")
workflow.add_edge("extract_document", "process_data")
workflow.add_edge("process_data", "analyze_result")
workflow.add_edge("analyze_result", END)

# Run the graph
inputs = {"messages": ["DOC123"]}  # Assume DOC123 is a valid document ID in Instabase
for output in workflow.stream(inputs):
    print(output)