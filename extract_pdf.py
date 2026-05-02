import sys
import PyPDF2

def extract_text(pdf_path, output_path):
    text = ''
    try:
        import fitz
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + '\n'
    except Exception as e:
        print(f"Error reading with PyMuPDF: {e}")
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + '\n'
        except Exception as e2:
            print(f"Error reading with PyPDF2: {e2}")
            return
            
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extraction successful. Output written to {output_path}")

if __name__ == "__main__":
    extract_text(sys.argv[1], sys.argv[2])
