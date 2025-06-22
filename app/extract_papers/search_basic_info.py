import requests
from dotenv import load_dotenv
import os
import csv
import logging
import sqlite3
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_research_length(headers: dict, url: str, query: str, subject: str, scopus_api: str) -> int:
    """
    Gets the total number of results for the query.
    Gets the total number of results for the query and save it to research_length
    See https://dev.elsevier.com/sc_search_views.html for more details on the Scopus API search
    The count parameter is initially "manualy" set to 1 to get the total number of results without retrieving all entries
    """

    params = {
        "query": query,
        "subj" : subject,
        "count": 1,
        "apiKey": scopus_api,
        "httpAccept": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)
    research_length = int(response.json().get("search-results").get("opensearch:totalResults"))
    return research_length

def get_papers(headers: dict, url: str, query: str, subject: str, scopus_api: str, research_length: int, count: int) -> list:
    """
    Retrieves papers from the Scopus API based on the provided query and subject.
    Loops through the results in chunks of 'count' until it reaches the total number of results.
    Extracts relevant information from each entry in the chunk and appends it to a list.    
    """
    papers = []
    retrieved = 0
    # Loop through the results in chunks of 'count' until we reach the total number of results
    for start in range(0, research_length, count):
        params = {
        "query": query,
        "subj" : subject,
        "count": count,
        "start": start,
        "apiKey": scopus_api,
        "httpAccept": "application/json"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Scopus API request failed with status code {response.status_code}: {response.text}")
        data = response.json()
        retrieved += len(data.get("search-results", {}).get("entry", []))
        logging.info(f"Retrieved {len(data.get('search-results', {}).get('entry', []))} entries out of {research_length}, from Scopus API starting at {start}")

        # Extract relevant information from each entry in the chunk
        for entry in data.get("search-results", {}).get("entry", []):
            # Extract all links as a single string (comma-separated)
            links = entry.get("link", [])
            links_str = "; ".join([f"{l.get('@ref')}: {l.get('@href')}" for l in links]) if links else ""
            papers.append({
                "eid": entry.get("eid"),
                "dc_identifier": entry.get("dc:identifier"),
                "prism_url": entry.get("prism:url"),
                "prism_doi": entry.get("prism:doi", ""),
                "links": links_str,
                "title": entry.get("dc:title")
            })
    return papers

def save_papers_to_csv(papers: list, csv_file_name: str):
    """Saves the list of papers to a CSV file."""
    fieldnames = list(papers[0].keys())
    csv_file = csv_file_name
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper)

    print(f"Saved {len(papers)} papers to {csv_file}")


def create_db(db_file_name:str):
    """Create a SQLite database and a table for storing paper information."""
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            eid TEXT PRIMARY KEY,
            dc_identifier TEXT,
            prism_url TEXT,
            prism_doi TEXT,
            links TEXT,
            title TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_papers_to_db(db_file_name:str, papers:list):
    """Insert a list of papers into the SQLite database."""
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()
    for paper in papers:
        c.execute('''
            INSERT OR REPLACE INTO papers (eid, dc_identifier, prism_url, prism_doi, links, title)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            paper["eid"],
            paper["dc_identifier"],
            paper["prism_url"],
            paper["prism_doi"],
            paper["links"],
            paper["title"]
        ))

    conn.commit()
    conn.close()
    print(f"Saved {len(papers)} papers to {db_file_name}")


if __name__ == "__main__":
    load_dotenv()

    scopus_api = os.getenv("SCOPUS_API_KEY")

    # Configuration. Tailor these parameters to your needs
    # See https://dev.elsevier.com/scopus_api.html for more details on the Scopus API search
    # See https://dev.elsevier.com/sc_search_views.html for more details on the Scopus API parameters
    url = "https://api.elsevier.com/content/search/scopus"
    query = 'TITLE-ABS-KEY( "policy implementation" OR "instrument implementation" OR "program implementation") AND TITLE-ABS (driv* OR moderat* OR obstacle* OR mediat* OR imped* OR determin* OR issue* OR challeng* OR problem* OR barrier* OR facilit* OR enabl* OR factor*) AND TITLE ("implementation") AND LIMIT-TO ( SUBJAREA,"SOCI" )'
    count = 200 # the scopus API has a maximum of 200 results per request
    subject = "SOCI"  # Sociology subject area
    csv_file_name = "scopus_results.csv" # Use if you want to save the results to a CSV file
    db_file_name = "scopus_results.db"

    headers = {
        "X-ELS-APIKey": scopus_api,
        "Accept": "application/json"
    }
    research_lenght = get_research_length(headers, url, query, subject, scopus_api)
    papers = get_papers(headers, url, query, subject, scopus_api, research_lenght, count)
    # if you want to save the results to a CSV file
    #save_papers_to_csv(papers, csv_file_name)

    # If you want to save the results to a SQLite database
    # Create a SQLite database and a table for storing paper information
    create_db(db_file_name)
    insert_papers_to_db(db_file_name, papers)