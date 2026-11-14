'''pdf_processor.py
Utility to extract raw text from a PDF file using PyMuPDF (fitz).
The function is defensive – it returns an empty string for unreadable PDFs
and logs the cause for debugging.
''' 

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union
import io

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # PyMuPDF fallback

_logger = logging.getLogger(__name__)
if not _logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[pdf_processor] %(levelname)s: %(message)s'))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


def extract_text_from_pdf(source: Union[str, Path, bytes, io.BytesIO]) -> str:
    """Extract plain text from a PDF.

    Parameters
    ----------
    source : str, pathlib.Path, bytes, or file-like object
        File path to the PDF document, or raw bytes / stream (e.g. from Streamlit).

    Returns
    -------
    str
        Concatenated textual content of all readable pages.  Returns an empty
        string if the file cannot be opened or contains no extractable text.
    """
    try:
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.is_file():
                _logger.error("File not found: %s", path)
                return ""
            doc = fitz.open(str(path))
        elif isinstance(source, bytes):
            doc = fitz.open(stream=source, filetype="pdf")
        elif hasattr(source, "read"):
            data = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
            doc = fitz.open(stream=data, filetype="pdf")
        else:
            _logger.error("Unsupported PDF source type: %s", type(source))
            return ""
    except Exception as exc:
        _logger.error("Failed to open PDF source: %s", exc)
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

