import pymysql
import requests
import dotenv
from langchain_core.tools import tool
import os
import streamlit as st
dotenv.load_dotenv()


from tavily import TavilyClient
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


serpapi_params = {
    "engine": "google",
    "api_key": os.getenv("SERPAPI_KEY")
}




@tool
def web_search(query: str):
    """Finds general knowledge information using Google search. Can also be used
    to find to search about CO2 emission of items that we are calculating"""
    search =client.search(query, search_depth="advanced")["results"]
    return search



@tool
def environment_database(materialname:str):
    """Returns the amount of CO2 emitted by producing 1 Kg of a particular item"""

    try:
        # Connect to the database
        conn = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["db"],
            port=int(st.secrets["mysql"]["port"]),
            charset=(st.secrets["mysql"]["charset"]),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
            read_timeout=10,
            write_timeout=10
        )

        with conn.cursor() as cursor:
            # Use parameterized query to avoid SQL injection
            query = "SELECT emmission_factor FROM materials WHERE LOWER(material_name) = %s"
            cursor.execute(query, (materialname.lower(),))
            output = cursor.fetchone()

        # If no result is found
        if output:
            return output['emmission_factor']
        else:
            return "Material not found use search tool"
    
    except pymysql.MySQLError as e:
        st.error(f"Database error: {e}")
        return None
    
    finally:
        # Ensure the connection is closed even if an error occurs
        if conn:
            conn.close()


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

