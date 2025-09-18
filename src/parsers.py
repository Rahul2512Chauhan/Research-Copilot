import re
import fitz
import pytesseract
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO , format="%(levelname)s: %(message)s")

def clean_text(text: str) -> str:
    if not text:
        return ""
    #Normlaize spaces and newlines
    text = text.replace("\xa0" , " ") #non_breaking spaces
    text = re.sub(r"\s+" , " " , text) #collapse multiple whitespace
    return text.strip()

def is_scanned_page(page) -> bool:
    """Return True if page has no extractable text."""
    text = page.get_text("text")
    return len(text.strip()) == 0

def render_page_image(page, dpi: int = 300) -> Image.Image:
    """Render a PDF page into a PIL image for OCR."""
    mat = fitz.Matrix(dpi / 72 ,dpi /72) #scale to DPI
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))

def ocr_page(page) -> str:
    """Run OCR on a page by rendering to image and passing to Tesseract."""
    image = render_page_image(page)
    text = pytesseract.image_to_string(image , lang="eng")
    return clean_text(text)

def parse_pdf_to_pages(file_path: str, source_id: str) -> list[dict]:
    """
    Parse a PDF into structured page dicts.
    Each dict is ready to insert into the `pages` table.
    """

    pages_data = []

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        logging.error(f"❌ Failed to open PDF {file_path}: {e}")
        return pages_data
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = ""
        used_ocr = False
        errors = 0

        try:
            # Try native extraction
            if not is_scanned_page(page):
                text = clean_text(page.get_text("text")) # type: ignore
            else:
                # OCR fallback
                used_ocr = True
                text = ocr_page(page)

        except Exception as e:
            logging.error(f"❌ Error parsing page {page_num+1} of {file_path}: {e}")
            errors += 1
            text = ""

        word_count = len(text.split()) if text else 0

        page_record = {
            "source_id": source_id,
            "page_number": page_num + 1,
            "text": text,
            "word_count": word_count,
            "ocr": used_ocr,
            "parse_errors": errors,
            }
        pages_data.append(page_record)

    logging.info(f"✅ Parsed {len(pages_data)} pages from {file_path}")
    return pages_data
        

