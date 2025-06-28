import logging
from typing import Dict, List, Optional
import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import ModelRetry
import sqlite3
import time
from pathlib import Path

nest_asyncio.apply()  # for running with interactive python
# Set up logging
logging.basicConfig(
    level=logging.INFO)


class ResponseModel(BaseModel):
    """Structured response with metadata."""

    should_be_included: bool = Field(
        description="Indicates if the paper should be included in the review",
    )
    confidence_level: float = Field(
        description="Confidence level in the decision wether to include the paper in the review", ge=0, le=1
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


# Function to retrieve papers from the SQLite database
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


def process_and_update_papers(db_path: str, agent):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    cursor.execute("SELECT eid, title, abstract FROM papers")
    total = 0
    for eid, title, abstract in cursor:
        paper = Paper(eid=eid, title=title, abstract=abstract)
        logging.info(f"Processing paper: {title}")
        response = agent.run_sync(user_prompt="Retrieve the structured output", deps=paper)
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


if __name__ == "__main__":
    logging.info("Starting paper analysis...")

    # Config:
    instruction_file = Path(__file__).parent.parent.parent / "resources" / "screening_promt.txt"
    db_dir = str(Path(__file__).parent.parent)
    db_path = db_dir + "\\scopus_results_2.db"


    with open(instruction_file, "r", encoding="utf-8") as file:
        instructions_text = file.read()

    # Agent with structured output and dependencies
    agent = Agent(
        model="openai:gpt-4.1",
        output_type=ResponseModel,
        deps_type=Paper,
        retries=3,
        message_history=None,
        instructions=instructions_text,
    )


    # Add dynamic system prompt based on dependencies
    @agent.system_prompt
    async def analyse_paper(ctx: RunContext[Paper]) -> str:
        return f"Paper: {ctx.deps}"

    ensure_columns_exist(db_path)
    process_and_update_papers(db_path, agent)