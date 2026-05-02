import fitz
import os
import re

def extract_pdf_content(pdf_path, output_image_dir, prefix="img"):
    """
    Extracts text and images from a PDF.
    Returns the text with image placeholders like [IMAGE: img_name.png] inserted near where they appeared.
    """
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)
        
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # We can extract text blocks
        blocks = page.get_text("blocks")
        
        # Sort blocks by vertical position (y0), then horizontal (x0)
        blocks.sort(key=lambda b: (b[1], b[0]))
        
        # Extract images
        image_list = page.get_images(full=True)
        images_info = []
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            
            # Filter out tiny UI icons/logos
            if base_image.get("width", 0) < 100 or base_image.get("height", 0) < 100:
                continue
                
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"{prefix}_p{page_num+1}_{img_index+1}.{image_ext}"
            image_path = os.path.join(output_image_dir, image_filename)
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
                
            # Try to find the image bounding box to interleave with text
            img_rects = page.get_image_rects(xref)
            if img_rects:
                # Use the first rect
                y0 = img_rects[0].y0
                images_info.append({"filename": image_filename, "y0": y0})
            else:
                images_info.append({"filename": image_filename, "y0": 0})
                
        # Interleave text and images based on vertical position
        content_items = []
        for b in blocks:
            # text blocks have the format (x0, y0, x1, y1, "text", block_no, block_type)
            # block_type == 0 means text
            if b[6] == 0:
                text = b[4].strip()
                if text:
                    content_items.append({"type": "text", "y0": b[1], "content": text})
                    
        for img_info in images_info:
            content_items.append({"type": "image", "y0": img_info["y0"], "content": f"[IMAGE: {img_info['filename']}]"})
            
        content_items.sort(key=lambda item: item["y0"])
        
        page_text = f"--- Page {page_num+1} ---\n"
        for item in content_items:
            page_text += item["content"] + "\n\n"
            
        full_text.append(page_text)
        
    return "\n".join(full_text)

def process_all_reports(sample_report_path, thermal_report_path, output_image_dir):
    sample_content = extract_pdf_content(sample_report_path, output_image_dir, prefix="sample")
    thermal_content = extract_pdf_content(thermal_report_path, output_image_dir, prefix="thermal")
    return sample_content, thermal_content

if __name__ == "__main__":
    s, t = process_all_reports("Sample Report.pdf", "Thermal Images.pdf", "images")
    with open("extracted_data.txt", "w", encoding="utf-8") as f:
        f.write("=== SAMPLE REPORT ===\n" + s + "\n\n=== THERMAL IMAGES ===\n" + t)
    print("Extraction complete. Check extracted_data.txt and the images/ folder.")
