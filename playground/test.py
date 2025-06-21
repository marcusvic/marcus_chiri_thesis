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
    title: str
    implementation_performance: Literal["Mixed Outcome", "Failure", "Success"] = Field(
        description="Performance of the policy implementation"
    )
    text_excerpt_for_implementation_performance: Optional[str] = Field(
        description="This field should be filled with the reason for the implementation performance, by providing a text excerpt from the policy document that explains the performance."
    )
    Political_salience_or_prioritization_or_comittment_or_support: Optional[bool] = (
        Field(
            description="Support/committment etc. of high-level politicians is coded with this code. Example when this would be true: The president of a country has discovered their passion for animal welfare and uses their power to motivate the government to engage in a wide variety of activities. Our animal welfare label is implemented in that context and the authors argue that the committment of the president has helped the implementation process"
        )
    )
    text_excerpt_for_political_salience_or_prioritization_or_comittment_or_support: Optional[
        str
    ] = Field(
        description="If Political_salience_or_prioritization_or_comittment_or_support is True, then this field should be filled with the reason for the political salience, prioritization, committment or support, by providing a text excerpt from the policy document that explains the political salience, prioritization, committment or support."
    )
    cross_boundary_issue: Optional[bool] = Field(
        description="Many policy problems span across various types of boundaries such as national borders, jurisdictions or sectoral boundaries. Example: One challenging aspect in this regard is the common separation of terrestrial and aquatic ecosystems in connectivity modeling and analysis, with most attention paid to large-scale terrestrial ecosystems. However, there will be a need to extend national corridor efforts beyond terrestrial systems, integrating freshwater and marine, especially along coastal areas."
    )
    text_excerpt_for_cross_boundary_issue: Optional[str] = Field(
        description="If cross_boundary_issue is True, then this field should be filled with the reason for the cross boundary issue, by providing a text excerpt from the policy document that explains the cross boundary issue."
    )
    availability_of_theory_and_technology: Optional[bool] = Field(
        description="Some problems are well understood, e.g. due to well established scientific research, others are simply easy to understand. Some problems have technology readily available to solve the issue."
    )
    text_excerpt_for_availability_of_theory_and_technology: Optional[str] = Field(
        description="If availability_of_theory_and_technology is True, then this field should be filled with the reason for the availability of theory and technology, by providing a text excerpt from the policy document that explains the availability of theory and technology."
    )
    diversity_of_target_group_behaviour: Optional[bool] = Field(
        description="Return True if the behaviour of the target group is very diverse, e.g. because people have different reasons/motivations to behave in a certain manner, then it becomes more difficult to find mechanisms that address these different behaviours in a balanced way."
    )
    text_excerpt_for_diversity_of_target_group_behaviour: Optional[str] = Field(
        description="If diversity_of_target_group_behaviour is True, then this field should be filled with the reason for the diversity of target group behaviour, by providing a text excerpt from the policy document that explains the diversity of target group behaviour."
    )
    extent_of_behavioral_change_required: Optional[bool] = Field(
        description="Example of a case when this would be True: The prevailing technology on arable land in Altai krai entails burning harvested crop residues, and tillage operations each season (combined tillage) with various wide blades or with knife tillers that cut the roots of weeds. In order to comply with the burning ban, farmers would need to change to a form of conservation tillage, used up to now on approximately only 5 percent of the cropland in the investigated area (Belajev, 2009). Farmers would face the following difficulties in tilling residue-laden fields: (A misfit in policy to protect Russia's black soil region, p. 523)"
    )
    text_excerpt_for_extent_of_behavioral_change_required: Optional[str] = Field(
        description="If extent_of_behavioral_change_required is True, then this field should be filled with the reason for the extent of behavioral change required, by providing a text excerpt from the policy document that explains the extent of behavioral change required."
    )
    timing_or_duration_or_sequencing: Optional[str] = Field(
        description="What was the timing, duration or sequencing of the policy?"
    )
    characteristics_of_responsible_government_actors: Optional[str] = Field(
        description="What skills, beliefs, values and other personality traits to the policymakers responsible for formulation have? And how does the behaviour that results from these characteristics affect implementation?"
    )
    responsiveness_of_policymakers_to_feedback: Optional[str] = Field(
        description="Do the inputs provided through consultation and feedback mechanisms actually influence the policy formulation process or are they ignored?"
    )
    consultation_or_feedback_opportunities: Optional[str] = Field(
        description="Feedback opportunities, such as public hearings, can increase acceptance or improve the design of measures. At the same time lengthy processes of consultation might also slow down. Example: When new protected areas are designated, a transparent process with participation of the local communities will posibly reduce the resistance of those communities, even though they may no longer be able to e.g., freely hunt or use timber."
    )
    level_of_conflict_among_actors_involved: Optional[str] = Field(
        description="Conflicts among stakeholders are influenced by different aspects such as the importance each stakeholder puts on the problem at hand, the goals to be achieved, or the tools used to achieve the goals. The larger the conflict, the more likely it is that policymakers develop an ambiguous policy statute to accomodate the different positions. Example: Taxing company profits is usually a policy area that high conflict in policy formulation. The result is a taxation that leaves a lot of opportunitiy for companies to reduce their profit through accounting methods."
    )
    perceived_legitimacy_of_process: Optional[str] = Field(
        description="If stakeholders, especially those affected by the policy, perceive the formulation of the policy as illegitimate they may resist compliance or sabotage implementation. Example: In BSMP, the participation of government agencies was not an issue; their superiors in the ministries appointed the participants. The agencies received co-ordinated mandates that ensured that the work would become policy relevant and certain budgets to hire consultants. This broad mobilization of knowledge from sectors with different interests created legitimacy. Policy-makers and stakeholders alike were therefore more inclined to accept the results as credible. (Ecosystem-based management in Canada and Norway, p. 493)"
    )
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


files_dir = Path(__file__).parent / "files"
results = []


for pdf_file in files_dir.glob("*.pdf"):
    with open(pdf_file, "rb") as f:
        reader = PdfReader(f)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() or ""

    logging.info(f"Processing file: {pdf_file.name}")
    agent1 = Agent(
        model="openai:gpt-4.1",
        output_type=PolicyAnalysis,
        instructions=(
            "You are a policy analyst. You are analysing a policy text and will categorise the policies according to the received output_type. Classify the policy text and return the output in the specified format."
        ),
    )

    response = agent1.run_sync(pdf_text)
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
