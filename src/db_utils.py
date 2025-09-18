from src.db import SessionLocal , Page
from src.parsers import parse_pdf_to_pages
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s : %(message)s")

def save_pages_to_db(pages: list[dict]) -> dict:
    """
    Save parsed pages to DB.
    Returns summary: {'success': n, 'failed': n}
    """

    db = SessionLocal()
    success, failed = 0 , 0

    for p in pages:
        try:
            page_obj = Page(
                source_id=p["source_id"],
                page_number=p["page_number"],
                text=p["text"],
                word_count=p["word_count"],
                ocr=p["ocr"],
                parse_errors=p["parse_errors"]
            )
            db.add(page_obj)
            success += 1
        except Exception as e:
            logging.error(f"❌ Failed to save page {p['page_number']} of {p['source_id']}: {e}")
            failed += 1

    try:
        db.commit()
    except Exception as e:
        logging.error(f"❌ Commit failed: {e}")
        db.rollback()
        failed += success
        success = 0
    finally:
        db.close()

    logging.info(f"✅ Saved {success} pages, failed {failed} pages")
    return {"success": success, "failed": failed}

def parse_and_store(file_path: str, source_id: str) -> dict:
    """
    Combines parsing + DB saving.
    """
    pages = parse_pdf_to_pages(file_path, source_id)
    if not pages:
        logging.warning(f"No pages parsed for {file_path}")
        return {"success": 0, "failed": 0}
    
    return save_pages_to_db(pages)
