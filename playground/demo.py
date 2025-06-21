from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pathlib import Path
from PyPDF2 import PdfReader
import os
import csv
import nest_asyncio
import logging

logging.basicConfig(level=logging.INFO)

nest_asyncio.apply()  # Apply nest_asyncio to allow nested event loops. This allows testing in Jupyter notebooks or similar environments.

# class LiteralExample(BaseModel):
#     status: Literal["pending", "approved", "rejected"]
#     role: Literal["admin", "user", "guest"] = "users"  # With default


class PolicyAnalysis(BaseModel):
    illicit_influence: Optional[str] = Field(
        description="These are methods of influence that are not allowed by the legal or political rules of a system (mostly corruption)"
    )


# agent1 = Agent(
#     model="openai:gpt-4.1",
#     output_type=PolicyAnalysis,
#     instructions=(
#         "You are a policy analyst. You are analysing a policy text and will categorise the policies according to the received output_type. Classify the policy text and return the output in the specified format."
#     ),
# )


# files_dir = Path(__file__).parent / "files"

# pdf_path = files_dir / "NorthernUK.pdf"

# with open(pdf_path, "rb") as f:
#         reader = PdfReader(f)
#         pdf_text = ""
#         for page in reader.pages:
#             pdf_text += page.extract_text() or ""

# response = agent1.run_sync(pdf_text)
# structured_output = response.output.model_dump_json(indent=2)
# print(response.output.model_dump_json(indent=2))


agent1 = Agent(
    model="openai:gpt-4.1",
    output_type=PolicyAnalysis,
    instructions=(
        "You are a policy analyst. You are analysing a policy text and will categorise the policies according to the received output_type. Classify the policy text and return the output in the specified format."
    ),
)

response = agent1.run_sync(
    "This is a test input to check if the agent is working correctly."
)
structured_output = response.output.model_dump_json(indent=2)
results.append({"filename": pdf_file.name, "output": structured_output})
logging.info(f"Processed file: {pdf_file.name}")

# Save results to CSV
csv_path = Path(__file__).parent / "policy_analysis_results.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["filename", "output"])
    writer.writeheader()
    for row in results:
        writer.writerow(row)
