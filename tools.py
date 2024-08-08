from langchain_core.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
import os 


load_dotenv()  

client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))







@tool
def search(query: str):
    """Call to surf the web."""
    result = client.search(query, include_answer=True)
    output = result["answer"]
    return output


@tool
def pollution(expression: str):
    """Call to search for air pollution."""
    if expression == "Polyester":
        output = 3.5
    elif expression == "Cotton":
        output = 5
    elif expression == "Silk":
        output = 2
    elif expression == "Wool":
        output = 4
    else:
        output = "Not found"
        return output
    




@tool
def calculator(expressiona: int, expressionb: int, operator: str):
    """Call to perform calculations."""
    if operator == "add":
        output = expressiona + expressionb
    elif operator == "subtract":
        output = expressiona - expressionb
    elif operator == "multiply":
        output = expressiona * expressionb
    elif operator == "divide":
        output = expressiona / expressionb
    else:
        output = "Not found"
        return output




