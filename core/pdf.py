from pathlib import Path
from pypdf import PdfReader


def extract_pdf_text(pdf_path: Path, output_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    chunks = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        chunks.append(f"\n\n===== PAGE {i} =====\n{text}")

    full_text = "".join(chunks)
    output_path.write_text(full_text, encoding="utf-8")
    return full_text
