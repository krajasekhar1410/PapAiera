import os
from pypdf import PdfReader

docs_dir = r"c:\Users\Rajasekhar K\OneDrive\Desktop\Myapps\PapAiEra\docs"
pdfs = [
    "2019J6_Rippon_IECR.pdf",
    "ABB 2sigma.pdf",
    "InTech-Model_predictive_control_and_optimization_for_papermaking_processes.pdf"
]

output_file = "new_pdf_contents.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for pdf_file in pdfs:
        pdf_path = os.path.join(docs_dir, pdf_file)
        f.write(f"--- {pdf_file} ---\n")
        print(f"Reading {pdf_file}...")
        try:
            reader = PdfReader(pdf_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                f.write(f"Page {i+1}:\n")
                if text:
                    f.write(text + "\n")
        except Exception as e:
            f.write(f"Error reading {pdf_file}: {e}\n")
        f.write("\n" + "="*50 + "\n")

print(f"Done! Contents written to {output_file}")
