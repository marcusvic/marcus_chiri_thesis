import sqlite3
import requests
import os
from dotenv import load_dotenv
import time
import logging
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Load API key
load_dotenv()
api_key = os.getenv("SCOPUS_API_KEY")

headers = {
    "X-ELS-APIKey": api_key,
    "Accept": "application/json"
}

# Connect to the database
db_file_name = "scopus_results.db"
conn = sqlite3.connect(db_file_name)
c = conn.cursor()

# Add an 'abstract' column if it doesn't exist
c.execute("PRAGMA table_info(papers)")
columns = [col[1] for col in c.fetchall()]
if "abstract" not in columns:
    c.execute("ALTER TABLE papers ADD COLUMN abstract TEXT")

# Get all EIDs
c.execute("SELECT eid FROM papers")
eids = [row[0] for row in c.fetchall()]

counter = 0
for eid in eids:
    url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    response = requests.get(url, headers=headers)
    counter += 1
    logging.info(f"Processing {counter}/{len(eids)}: {eid}")
    if response.status_code == 200:
        data = response.json()
        # Try to extract the abstract
        abstract = ""
        try:
            abstract = data["abstracts-retrieval-response"]["coredata"].get("dc:description", "")
        except Exception:
            pass
        # Update the database
        c.execute("UPDATE papers SET abstract = ? WHERE eid = ?", (abstract, eid))
        logging.info(f"Updated abstract for {eid}")
    else:
        print(f"Failed to retrieve abstract for {eid}: {response.status_code}")
    time.sleep(0.2)  # Be polite to the API

conn.commit()
conn.close()
print("All abstracts updated.")