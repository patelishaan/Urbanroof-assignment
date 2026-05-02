import os
import json
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

def convert_html_to_pdf(source_html, output_filename):
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(
            source_html,
            dest=result_file
        )
    return pisa_status.err

def generate_report(json_path, template_dir, template_name, output_pdf, image_dir):
    with open(json_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    # Convert relative image dir to absolute for xhtml2pdf to reliably load them
    abs_image_dir = os.path.abspath(image_dir).replace('\\', '/')
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    html_out = template.render(report=report_data, image_dir=abs_image_dir)
    
    err = convert_html_to_pdf(html_out, output_pdf)
    if err:
        print(f"Error generating PDF.")
    else:
        print(f"Successfully generated {output_pdf}")

if __name__ == "__main__":
    generate_report(
        json_path="report_data.json",
        template_dir="templates",
        template_name="report_template.html",
        output_pdf="Generated_Main_DDR.pdf",
        image_dir="images"
    )
