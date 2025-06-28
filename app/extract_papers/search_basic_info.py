import requests
from dotenv import load_dotenv
import os
import csv
import logging
import sqlite3
from pathlib import Path
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

def get_papers(headers: dict, url: str, query: str, subject: str, scopus_api: str, research_length: int, chunk: int) -> list:
    """
    Retrieves papers from the Scopus API based on the provided query and subject.
    Loops through the results in chunks of 'chunk' until it reaches the total number of results.
    Extracts relevant information from each entry in the chunk and appends it to a list.    
    """
    papers = []
    retrieved = 0
    # Loop through the results in chunks of 'chunk' until we reach the total number of results
    for start in range(0, research_length, chunk):
        params = {
        "query": query,
        "subj" : subject,
        "count": chunk,
        "start": start,
        "apiKey": scopus_api,
        "httpAccept": "application/json"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Scopus API request failed with status code {response.status_code}: {response.text}")
        data = response.json()
        retrieved += len(data.get("search-results", {}).get("entry", []))
        logging.info(f"Retrieved {retrieved} / {research_length} from Scopus API.")

        # Extract relevant information from each entry in the chunk
        for entry in data.get("search-results", {}).get("entry", []):
            papers.append({
                "eid": entry.get("eid"),
                "scopus_id": entry.get("dc:identifier"),
                "first_author": entry.get("dc:creator"),
                "content_retrieval_uri": entry.get("prism:url"),
                "prism_doi": entry.get("prism:doi", ""),
                "link_self": entry.get("link")[0].get("@href"),
                "link_author_affiliation": entry.get("link")[1].get("@href"),
                "link_scopus": entry.get("link")[2].get("@href"),
                "open_access": entry.get("openaccess", ""),
                "openaccessFlag": entry.get("openaccessFlag", ""),
                "suptype": entry.get("subtypeDescription"),
                "suptype_code": entry.get("subtype"),
                "citedby-count": entry.get("citedby-count"),
                "source_title": entry.get("prism:publicationName"),
                "prism_issn": entry.get("prism:issn"),
                "prism_isbn": entry.get("prism:isbn"),
                "publication_date": entry.get("prism:coverDate"),
                "pii": entry.get("pii"),
                "pubmed-id": entry.get("pubmed-id"),
                "orcid": entry.get("orcid"),
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
            scopus_id TEXT,
            first_author TEXT,
            content_retrieval_uri TEXT,
            prism_doi TEXT,
            link_self TEXT,
            link_author_affiliation TEXT,
            link_scopus TEXT,
            open_access TEXT,
            openaccessFlag BOOLEAN,
            suptype TEXT,
            suptype_code TEXT,
            citedby_count INTEGER,
            source_title TEXT,
            prism_issn TEXT,
            prism_isbn TEXT,
            publication_date DATE,
            pii TEXT,
            pubmed_id TEXT,
            orcid TEXT,
            title TEXT)
    ''')
    conn.commit()
    conn.close()

def insert_papers_to_db(db_file_name:str, papers:list):
    """Insert a list of papers into the SQLite database."""
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()
    try:
        for paper in papers:
            c.execute('''
                INSERT OR REPLACE INTO papers (eid,
                scopus_id,
                first_author,
                content_retrieval_uri,
                prism_doi,
                link_self,
                link_author_affiliation,
                link_scopus,
                open_access,
                openaccessFlag,
                suptype,
                suptype_code,
                citedby_count,
                source_title,
                prism_issn,
                publication_date,
                pii,
                pubmed_id,
                orcid,
                title
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper["eid"],
                paper["scopus_id"],
                paper["first_author"],
                paper["content_retrieval_uri"],
                paper["prism_doi"],
                paper["link_self"],
                paper["link_author_affiliation"],
                paper["link_scopus"],
                paper["open_access"],
                paper["openaccessFlag"],
                paper["suptype"],
                paper["suptype_code"],
                paper["citedby-count"],
                paper["source_title"],
                paper["prism_issn"],
                paper["publication_date"],
                paper["pii"],
                paper["pubmed-id"],
                paper["orcid"],
                paper["title"]
            )
            )
        conn.commit()
        logging.info(f"Saved {len(papers)} papers to {db_file_name}")
    finally:
        conn.close()
    


if __name__ == "__main__":
    load_dotenv()

    scopus_api = os.getenv("SCOPUS_API_KEY")

    # Configuration. Tailor these parameters to your needs
    # See https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl for more details on the Scopus API search
    # See https://dev.elsevier.com/sc_search_views.html for more details on the Scopus API parameters
    url = "https://api.elsevier.com/content/search/scopus"
    query = 'TITLE-ABS-KEY( "policy implementation" OR "instrument implementation" OR "program implementation") AND TITLE-ABS (driv* OR moderat* OR obstacle* OR mediat* OR imped* OR determin* OR issue* OR challeng* OR problem* OR barrier* OR facilit* OR enabl* OR factor*) AND TITLE ("implementation") AND LIMIT-TO ( SUBJAREA,"SOCI" )'
    #you can only use 200 if you're connected to the institutional network, otherwise you can only use 25
    chunk = 200 # the scopus API has a maximum of 200 results per request
    subject = "SOCI"  # Sociology subject area
    csv_file_name = "scopus_results.csv" # Use if you want to save the results to a CSV file
    db_file_name = "scopus_results_2.db"

    # Some more static config    
    db_path = Path(__file__).parent.parent / db_file_name
    headers = {
        "X-ELS-APIKey": scopus_api,
        "Accept": "application/json"
    }

    #run the functions
    research_lenght = get_research_length(headers, url, query, subject, scopus_api)
    papers = get_papers(headers, url, query, subject, scopus_api, research_lenght, chunk)
    # if you want to save the results to a CSV file
    #save_papers_to_csv(papers, csv_file_name)

    # If you want to save the results to a SQLite database
    # Create a SQLite database and a table for storing paper information
    create_db(db_path)
    insert_papers_to_db(db_path, papers)