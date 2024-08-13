import requests
import dotenv
from langchain_core.tools import tool
import os

dotenv.load_dotenv()

import mysql.connector

from tavily import TavilyClient
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Nilesh.Tiwari1",
    database="environmental_data"

)



@tool
def web_search(query: str):
    """Finds general knowledge information using Google search. Can also be used
    to find to search about CO2 emission of items that we are calculating"""
    search =client.search(query, search_depth="advanced")["results"]
    return search



@tool
def environment_database(material_name:str):
    """Returns the amount of CO2 emitted by producing 1 Kg of a particular item"""
    if conn.is_connected():
        cursor = conn.cursor()
    else:
        # Reconnect to the database
        conn.reconnect(attempts=3, delay=5)
        cursor = conn.cursor()

    query = "SELECT pollution_index FROM materials WHERE material_name = %s"
    cursor.execute(query, (material_name.lower(),))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else "Not found use search tool"
    


@tool
def final_answer(
    research_steps: str,
    sources: str
):
    """Returns a natural language format response to the user in the form of a search result. There are several sections to this report, those are:
    - `search_result`: a paragraph summarizing the highquality result of query
    - `sustainable_nudge`: this is you should provide nudge towards the the option with less CO2 emissions, You can 
    calculate to show the amount of CO2 can be saved.
    - `sources`: a bulletpoint list provided detailed sources for all information
    referenced during the search process

    """
    if type(research_steps) is list:
        research_steps = "\n".join([f"- {r}" for r in research_steps])
    if type(sources) is list:
        sources = "\n".join([f"- {s}" for s in sources])
    return ""






@tool
def get_distance(origin: str, destination:str):
    """Returns the distance between two locations. Use the format: Origin: [origin], Destination: [destination]"""
    # Replace with your API key
    api_key = os.getenv("GOOGLE_MAPS_KEY")


    # Construct the API request URL
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={api_key}'

    # Send the API request
    response = requests.get(url)

    # Parse the JSON response
    data = response.json()

    # Extract the distance and duration
    distance = data['rows'][0]['elements'][0]['distance']['text']
    return distance

