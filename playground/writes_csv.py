import csv
import json
from pathlib import Path

input_csv = Path(__file__).parent / "policy_analysis_results.csv"
output_csv = Path(__file__).parent / "policy_analysis_results_expanded.csv"

rows = []
all_keys = set()

# Read the CSV and collect all keys from the JSON in the 'output' column
with open(input_csv, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        output_json = json.loads(row["output"])
        row_data = {"filename": row["filename"], **output_json}
        rows.append(row_data)
        all_keys.update(output_json.keys())

# Prepare the header: filename + all JSON keys
fieldnames = ["filename"] + sorted(all_keys)

# Write the expanded CSV
with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
