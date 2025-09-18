import streamlit as st
from src.utils import ensure_unique_source_id, save_pdf_bytes, is_pdf_bytes
from src.db import SessionLocal, Source
from src.db_utils import parse_and_store
from datetime import datetime, timezone

st.title("Research Copilot - PDF Upload (v1)")

# File uploader
uploaded_files = st.file_uploader(
    "Upload PDFs (max 3)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 3:
        st.warning("You can upload a maximum of 3 PDFs at a time.")
    else:
        db = SessionLocal()
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()

            # Validate PDF
            if not is_pdf_bytes(file_bytes):
                st.error(f"{uploaded_file.name} does not look like a valid PDF.")
                continue

            # Generate a unique source_id using DB
            source_id = ensure_unique_source_id(db)

            # Save PDF to storage/
            save_path = save_pdf_bytes(file_bytes, source_id)

            # Insert metadata into DB
            src = Source(
                source_id=source_id,
                filename=uploaded_file.name,
                uploaded_at=datetime.now(timezone.utc)
            )
            db.add(src)
            db.commit()

            # Parse PDF + save pages to DB
            result = parse_and_store(save_path, source_id)

            st.success(
                f"{uploaded_file.name} uploaded as {source_id} | "
                f"{result['success']} pages saved, {result['failed']} failed"
            )

            # --- Preview first page text ---
            if result['success'] > 0:
                from src.db import Page
                first_page = db.query(Page).filter_by(source_id=source_id, page_number=1).first()
                if first_page:
                    st.subheader("Preview: First Page")
                    st.text_area(
                        f"{uploaded_file.name} - Page 1",
                        first_page.text[:1000],  # show up to first 1000 chars
                        height=200
                    )
        db.close()

        st.info("All files processed and saved with unique source_ids.")
