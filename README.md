---
title: AI DDR Generator
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# AI Generalist | Applied AI Builder - DDR Generation

This repository contains the solution for the **Applied AI Builder (DDR Report Generation)** assignment. The goal of this project is to build an AI workflow that ingests raw site inspection documents and thermal reports (PDFs) and synthesizes them into a highly structured, client-ready **Detailed Diagnostic Report (DDR)**.

## Features & Compliance

This AI workflow was built to strictly adhere to the assignment requirements:
- **Multimodal Data Extraction**: Extracts both textual observations and relevant images from the provided PDFs. Small UI icons/logos are smartly filtered out to prevent LLM hallucination.
- **Logical Merging**: Combines findings from both the Inspection Report and Thermal Report without duplicate points.
- **Handling Incomplete Data**: Explicitly flags missing information as "Not Available" and handles conflicting details gracefully.
- **Structured Output**: Uses Gemini 2.5 Flash and Pydantic Structured Outputs to enforce a strict DDR schema (Summary, Area-wise Observations, Root Cause, Severity, Actions, Missing Info).
- **Client-Ready Report**: Assembles the parsed data and extracted images into a beautifully styled HTML template, converting it directly into a professional PDF output.
- **Generalized Approach**: The scripts are dynamic and will process any similar pair of inspection/thermal reports.

## Architecture

The system is divided into three main Python modules:
1. **`extractor.py`**: Uses `PyMuPDF` to parse the PDFs, extract text blocks, and pull high-quality images (ignoring tiny irrelevant icons). It interleaves images and text based on their coordinates in the PDF.
2. **`ai_processor.py`**: Feeds the interleaved data to **Gemini 2.5 Flash**. By leveraging `Pydantic` schemas, it forces the LLM to return a perfectly structured JSON object matching the requested DDR sections.
3. **`report_generator.py`**: Uses `Jinja2` to render the JSON data and actual image files into a styled HTML template (`templates/report_template.html`), and `xhtml2pdf` to convert the HTML into the final `Generated_Main_DDR.pdf`.

## Prerequisites

- Python 3.9+
- A Google Gemini API Key

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Environment**
   Rename `.env.example` to `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

1. Place your input reports (`Sample Report.pdf` and `Thermal Images.pdf`) in the root directory.
2. Run the main orchestrator script:
   ```bash
   python main.py
   ```
3. The script will:
   - Extract text and images (saving images to the `/images` folder).
   - Generate a `report_data.json` containing the AI's structured analysis.
   - Output the final, formatted PDF as `Generated_Main_DDR.pdf`.

## Technologies Used
- **Google GenAI SDK (Gemini 2.5 Flash)**: For advanced multimodal reasoning and JSON structuring.
- **PyMuPDF (fitz)**: For precise PDF text and image extraction.
- **Pydantic**: For strict schema validation of the LLM output.
- **Jinja2 & xhtml2pdf**: For templating and generating the final client-ready PDF report.

## Loom Video Presentation
*(Insert your Loom Video Link here)*
