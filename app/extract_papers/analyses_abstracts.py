import logging
from typing import Dict, List, Optional
import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import ModelRetry
import sqlite3
import time

nest_asyncio.apply()  # for running with interactive python
# Set up logging
logging.basicConfig(
    level=logging.INFO)


class ResponseModel(BaseModel):
    """Structured response with metadata."""

    should_be_analysed: bool = Field(
        description="Indicates if the paper should be analysed"
    )
    confidence_level: float = Field(
        description="Confidence level in the analysis decision", ge=0, le=1
    )
    summary: str = Field(
        description="Brief summary of the analysis decision",
        max_length=500,
    )


# Define order schema
class Paper(BaseModel):
    """Structure for each paper to be screened."""

    eid: str
    title: str
    abstract: str


# Agent with structured output and dependencies
agent3 = Agent(
    model="openai:gpt-4.1",
    output_type=ResponseModel,
    deps_type=Paper,
    retries=3,
    message_history=None,
    instructions="There are 2 ways of analysing policy implementation performance. Some papers analyse which factors caused the policy implementation performance (these are type A papers), and other papers analyse which effects a specific factor had in policy implementation performance (these are type B papers). We only want to analyse type A papers. Please exclude papers that focus solely on the effect of one particular variable on the outcome. You are receiving a list containing a paper's id, title and abstract. Output if the paper should be analysed or not (should_be_analysed), your confidence level between 0 and 1 in making this choice (confidence_level), and a very brief summary of why you made this choice (summary).",
)


# Add dynamic system prompt based on dependencies
@agent3.system_prompt
async def add_customer_name(ctx: RunContext[Paper]) -> str:
    return f"Customer details: {ctx.deps}"

# Function to retrieve papers from the SQLite database
from pathlib import Path
files_dir = str(Path(__file__).parent.parent)
db_path = files_dir + "\\scopus_results.db"

def ensure_columns_exist(db_path: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(papers)")
    columns = [col[1] for col in c.fetchall()]
    if "to_be_reviewed" not in columns:
        c.execute("ALTER TABLE papers ADD COLUMN to_be_reviewed BOOLEAN")
    if "confidence_level" not in columns:
        c.execute("ALTER TABLE papers ADD COLUMN confidence_level REAL")
    if "analysis_summary" not in columns:
        c.execute("ALTER TABLE papers ADD COLUMN analysis_summary TEXT")
    conn.commit()
    conn.close()


def process_and_update_papers(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    cursor.execute("SELECT eid, title, abstract FROM papers")
    total = 0
    for eid, title, abstract in cursor:
        paper = Paper(eid=eid, title=title, abstract=abstract)
        logging.info(f"Processing paper: {title}")
        response = agent3.run_sync(user_prompt="Retrieve the structured output", deps=paper)
        result = response.output
        # Store as bool (True/False)
        cursor2.execute(
            "UPDATE papers SET to_be_reviewed=?, confidence_level=?, analysis_summary=? WHERE eid=?",
            (bool(result.should_be_analysed), float(result.confidence_level), result.summary, eid)
        )
        conn.commit()
        total += 1
        logging.info(f"Processed {total} papers")
        time.sleep(0.2)
    conn.close()
    print(f"Processed and updated {total} papers.")    

# def get_papers_from_db(db_path: str, limit: int = 5):
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("SELECT eid, title, abstract FROM papers LIMIT ?", (limit,))
#     rows = cursor.fetchall()
#     conn.close()
#     papers = [{"eid": row[0], "title": row[1], "abstract": row[2]} for row in rows]
#     return papers

ensure_columns_exist(db_path)
process_and_update_papers(db_path)