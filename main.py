import os
from extractor import process_all_reports
from ai_processor import process_extracted_data
from report_generator import generate_report
from dotenv import load_dotenv
import json

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("Please set your GEMINI_API_KEY in the .env file.")
        return

    sample_pdf = "Sample Report.pdf"
    thermal_pdf = "Thermal Images.pdf"
    image_dir = "images"

    if not os.path.exists(sample_pdf) or not os.path.exists(thermal_pdf):
        print("Missing input PDF files in the current directory.")
        return

    print("Step 1: Extracting text and images from PDFs...")
    sample_text, thermal_text = process_all_reports(sample_pdf, thermal_pdf, image_dir)
    
    combined_text = f"=== SAMPLE REPORT ===\n{sample_text}\n\n=== THERMAL IMAGES ===\n{thermal_text}"
    with open("extracted_data.txt", "w", encoding="utf-8") as f:
        f.write(combined_text)

    print("Step 2: Processing data with Gemini AI...")
    report_data = process_extracted_data(combined_text)
    
    with open("report_data.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)

    print("Step 3: Generating PDF Report...")
    generate_report(
        json_path="report_data.json",
        template_dir="templates",
        template_name="report_template.html",
        output_pdf="Generated_Main_DDR.pdf",
        image_dir=image_dir
    )

    print("All done! The report has been generated at Generated_Main_DDR.pdf")

if __name__ == "__main__":
    main()
