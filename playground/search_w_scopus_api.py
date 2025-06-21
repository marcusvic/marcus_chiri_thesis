import requests
import urllib.parse
from dotenv import load_dotenv
import os
import csv

# Load environment variables from .env file
load_dotenv()

# Your Scopus API key from .env
API_KEY = os.getenv("SCOPUS_API_KEY")


# Scopus Search API endpoint
url = "https://api.elsevier.com/content/search/scopus"

# Your search query
query = 'TITLE-ABS-KEY( "policy implementation" OR "instrument implementation" OR "program implementation") AND TITLE-ABS (driv* OR moderat* OR obstacle* OR mediat* OR imped* OR determin* OR issue* OR challeng* OR problem* OR barrier* OR facilit* OR enabl* OR factor*) AND TITLE ("implementation") AND LIMIT-TO ( SUBJAREA,"SOCI" )'

# URL encode the query
params = {
    "query": query,
    "count": 100,  # Number of results to retrieve
    "apiKey": API_KEY,
    "httpAccept": "application/json"
}

headers = {
    "X-ELS-APIKey": API_KEY,
    "Accept": "application/json"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
data.get("search-results").get("entry")[1].get("dc:description")

papers = []
for entry in data.get("search-results", {}).get("entry", []):
    papers.append({
        "eid": entry.get("eid"),
        "title": entry.get("dc:title")
    })

csv_file = "scopus_results.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["eid", "title"])
    writer.writeheader()
    for paper in papers:
        writer.writerow(paper)

print(f"Saved {len(papers)} papers to {csv_file}")