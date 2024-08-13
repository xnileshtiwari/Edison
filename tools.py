import requests
import dotenv
from langchain_core.tools import tool
import os
from serpapi import GoogleSearch

dotenv.load_dotenv()

serpapi_params = {
    "engine": "google",
    "api_key": os.getenv("SERPAPI_KEY")
}
import mysql.connector


# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USERNAME"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB_NAME")
)



@tool
def web_search(query: str):
    """Finds general knowledge information using Google search. Can also be used
    to find to search about CO2 emission of items that we are calculating"""
    search = GoogleSearch({
        **serpapi_params,
        "q": query,
        "num": 5
    })
    results = search.get_dict()["organic_results"]
    contexts = "\n---\n".join(
        ["\n".join([x["title"], x["snippet"], x["link"]]) for x in results]
    )
    return contexts





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











