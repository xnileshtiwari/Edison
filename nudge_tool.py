import pymysql
import requests
import dotenv
from langchain_core.tools import tool
import os
import streamlit as st
dotenv.load_dotenv()


from tavily import TavilyClient
client = TavilyClient(api_key=st.secrets["api_keys"]["tavily"])




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
    introduction: str,
    research_steps: str,
    main_body: str,
    conclusion: str,
    sources: str
):
    """Returns a natural language format response to the user in the form of a research
    report. There are several sections to this report, those are:
    - `Environmental cost`: shows the main result in number of how much CO2 produced while creating this product.
    - `research_steps`: a few bullet points explaining the steps that were taken
    to research your report.
    - `main_body`: this is where the bulk of high quality and concise and detailed
    information about how you calculated CO2 emissions.
    - `conclusion`: this is a short single paragraph conclusion providing a
    concise but sophisticated view on what was found.
    - `sources`: a bulletpoint list provided detailed sources for all information
    referenced during the research process

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
    api_key = st.secrets["api_keys"]["google_maps"]


    # Construct the API request URL
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={api_key}'

    # Send the API request
    response = requests.get(url)

    # Parse the JSON response
    data = response.json()

    # Extract the distance and duration
    distance = data['rows'][0]['elements'][0]['distance']['text']
    return distance

