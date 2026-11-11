'''pdf_processor.py
Utility to extract raw text from a PDF file using PyMuPDF (fitz).
The function is defensive – it returns an empty string for unreadable PDFs
and logs the cause for debugging.
''' 

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union

import fitz  # PyMuPDF

_logger = logging.getLogger(__name__)
if not _logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[pdf_processor] %(levelname)s: %(message)s'))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


def extract_text_from_pdf(file_path: Union[str, Path]) -> str:
    """Extract plain text from a PDF.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Path to the uploaded PDF document.

    Returns
    -------
    str
        Concatenated textual content of all readable pages.  Returns an empty
        string if the file cannot be opened or contains no extractable text.
    """
    path = Path(file_path)
    if not path.is_file():
        _logger.error("File not found: %s", path)
        return ""
    try:
        doc = fitz.open(str(path))
    except Exception as exc:  # pragma: no cover – very rare, but guard anyway
        _logger.error("Failed to open PDF %s: %s", path, exc)
        return ""

    texts = []
    for page_num in range(doc.page_count):
        try:
            page = doc.load_page(page_num)
            txt = page.get_text("text").strip()
            if txt:
                texts.append(txt)
        except Exception as exc:  # pragma: no cover – handle corrupt pages
            _logger.warning("Could not read page %d of %s: %s", page_num, path, exc)
            continue
    doc.close()

    combined = "\n\n".join(texts)
    if not combined:
        _logger.info("PDF %s contained no extractable text.", path)
    return combined

