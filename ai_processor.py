import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types

# Pydantic Schemas
class Observation(BaseModel):
    area: str = Field(description="The specific area or location of the observation.")
    finding: str = Field(description="The textual observation, finding, or issue described.")
    image_filename: Optional[str] = Field(description="The exact filename of the image corresponding to this observation. E.g. [IMAGE: img_name.png] -> img_name.png. If none, leave null.")

class DDRReport(BaseModel):
    summary: str = Field(description="Property Issue Summary.")
    observations: List[Observation] = Field(description="List of all area-wise observations extracted from text and images.")
    root_cause: str = Field(description="Probable Root Cause across all observations.")
    severity: str = Field(description="Severity Assessment with reasoning.")
    recommended_actions: str = Field(description="Recommended Actions to mitigate the issues.")
    additional_notes: str = Field(description="Any additional notes.")
    missing_info: str = Field(description="Missing or Unclear Information. Explicitly write 'Not Available' if missing.")

def process_extracted_data(data_text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an AI assistant tasked with generating a Main Detailed Diagnostic Report (DDR) from raw site inspection documents and thermal reports.
    You will be provided with the extracted text from these documents. The text includes image references in the format [IMAGE: filename.ext].
    
    Important Rules:
    - Extract all relevant observations.
    - Combine information logically and avoid duplicate points.
    - If information conflicts -> mention the conflict.
    - If information is missing -> write "Not Available" in the missing_info field.
    - For each observation, determine if there is a corresponding image based on proximity to the text and include the EXACT filename (without the [IMAGE: ] part). If no image is mentioned for an observation, or if it says Image Not Available, set image_filename to None.
    - Do NOT invent facts not present in the documents.
    - Use simple, client-friendly language. Avoid unnecessary technical jargon.
    
    Here is the extracted data from the reports:
    
    {data_text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DDRReport,
            temperature=0.2,
        ),
    )
    
    return json.loads(response.text)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    with open("extracted_data.txt", "r", encoding="utf-8") as f:
        data = f.read()
    
    try:
        report = process_extracted_data(data)
        with open("report_data.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        print("AI Processing complete. Output written to report_data.json")
    except Exception as e:
        print(f"Error during AI Processing: {e}")
