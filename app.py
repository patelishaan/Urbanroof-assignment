import os
import uuid
import shutil
import io
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from extractor import process_all_reports
from ai_processor import process_extracted_data
from report_generator import generate_report
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-report', methods=['POST'])
def generate_report_api():
    if 'inspection_report' not in request.files or 'thermal_report' not in request.files:
        return jsonify({"error": "Missing PDF files"}), 400

    inspection_file = request.files['inspection_report']
    thermal_file = request.files['thermal_report']

    if inspection_file.filename == '' or thermal_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Create a unique job directory
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    image_dir = os.path.join(job_dir, 'images')
    os.makedirs(image_dir, exist_ok=True)

    try:
        # Save uploads
        sample_pdf_path = os.path.join(job_dir, secure_filename(inspection_file.filename))
        thermal_pdf_path = os.path.join(job_dir, secure_filename(thermal_file.filename))
        
        inspection_file.save(sample_pdf_path)
        thermal_file.save(thermal_pdf_path)

        # 1. Extract
        sample_text, thermal_text = process_all_reports(sample_pdf_path, thermal_pdf_path, image_dir)
        combined_text = f"=== SAMPLE REPORT ===\n{sample_text}\n\n=== THERMAL IMAGES ===\n{thermal_text}"

        # 2. AI Processing
        import json
        report_data = process_extracted_data(combined_text)
        json_path = os.path.join(job_dir, "report_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)

        # 3. Generate PDF
        output_pdf_path = os.path.join(job_dir, "Generated_Main_DDR.pdf")
        generate_report(
            json_path=json_path,
            template_dir="templates",
            template_name="report_template.html",
            output_pdf=output_pdf_path,
            image_dir=image_dir
        )

        # 4. Read generated PDF into memory so we can safely delete the job folder
        with open(output_pdf_path, 'rb') as f:
            pdf_data = f.read()

        mem_file = io.BytesIO(pdf_data)
        mem_file.seek(0)

        # Cleanup the entire job directory to save space on Render
        shutil.rmtree(job_dir, ignore_errors=True)

        return send_file(
            mem_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Generated_Main_DDR.pdf'
        )

    except Exception as e:
        # Ensure cleanup on error too
        shutil.rmtree(job_dir, ignore_errors=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Used for local dev
    app.run(host='0.0.0.0', port=5000, debug=True)
