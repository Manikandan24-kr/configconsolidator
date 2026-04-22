import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from sqlalchemy.orm import Session as DBSession

from pdf_parser import extract_pdf
from extractor.pass1_categorise import categorise_section
from extractor.pass2_extract import extract_rules_for_category
from extractor.dedup import deduplicate_session_rules
from models import Session as SessionModel, UploadedFile, Rule, _uuid, _now

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/kriyadocs_uploads"))


def run_extraction_pipeline(session_id: str, db: DBSession) -> None:
    """
    Full two-pass extraction pipeline for a session.
    Updates session.status and progress throughout.
    Designed to run as a background task.
    """
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        return

    _update_session(db, session, status="extracting", progress=0, message="Starting extraction...")

    files = db.query(UploadedFile).filter(UploadedFile.session_id == session_id).all()
    if not files:
        _update_session(db, session, status="review", progress=100, message="No files to process.")
        return

    # Collect all rules per category across all PDFs before dedup
    rules_by_category: dict[str, list[dict]] = {}
    total_files = len(files)

    for file_idx, uploaded_file in enumerate(files):
        filepath = Path(uploaded_file.filepath)
        if not filepath.exists():
            _mark_file(db, uploaded_file, "failed", "File not found on disk")
            continue

        pct_base = int((file_idx / total_files) * 90)
        _update_session(
            db, session,
            progress=pct_base,
            message=f"Parsing {uploaded_file.filename} ({file_idx + 1}/{total_files})..."
        )
        _mark_file(db, uploaded_file, "processing")

        try:
            doc = extract_pdf(str(filepath))
        except Exception as e:
            _mark_file(db, uploaded_file, "failed", str(e))
            continue

        sections = doc.sections if doc.sections else []
        if not sections:
            # Treat entire document text as one section
            full_text = "\n".join(p.text for p in doc.pages if hasattr(p, "text"))
            if full_text.strip():
                sections = [type("S", (), {"title": doc.title, "content": full_text})()]

        total_sections = len(sections)
        for sec_idx, section in enumerate(sections):
            content = getattr(section, "content", "") or getattr(section, "text", "") or ""
            title = getattr(section, "title", "") or ""

            if not content.strip():
                continue

            sec_pct = pct_base + int((sec_idx / max(total_sections, 1)) * (90 / total_files))
            _update_session(
                db, session,
                progress=sec_pct,
                message=f"{uploaded_file.filename} — Pass 1: mapping '{title[:40]}'"
            )

            # Pass 1: which categories does this section contain?
            categories = categorise_section(content)
            if not categories:
                continue

            # Pass 2: extract rules per category
            for category in categories:
                _update_session(
                    db, session,
                    progress=sec_pct,
                    message=f"{uploaded_file.filename} — Pass 2: extracting {category} from '{title[:30]}'"
                )
                extracted = extract_rules_for_category(content, category, source_section=title)
                for item in extracted:
                    item["source_document"] = uploaded_file.filename
                    item["category"] = category
                if extracted:
                    rules_by_category.setdefault(category, []).extend(extracted)

        _mark_file(db, uploaded_file, "done")

    # Deduplication across all categories
    _update_session(db, session, progress=92, message="Deduplicating rules...")
    rules_by_category = deduplicate_session_rules(rules_by_category)

    # Persist to DB
    _update_session(db, session, progress=95, message="Saving rules to database...")
    total_saved = 0
    for category, rule_list in rules_by_category.items():
        for order, item in enumerate(rule_list):
            rule = Rule(
                id=_uuid(),
                session_id=session_id,
                category=category,
                rule=item["rule"],
                source_document=item.get("source_document", ""),
                source_section=item.get("source_section", ""),
                remarks=item.get("remarks"),
                status="pending",
                is_custom=False,
                sort_order=order,
                created_at=_now(),
                updated_at=_now(),
            )
            db.add(rule)
            total_saved += 1

    session.total_rules = total_saved
    session.confirmed_rules = 0
    session.excluded_rules = 0
    db.commit()

    _update_session(
        db, session,
        status="review",
        progress=100,
        message=f"Extraction complete. {total_saved} rules extracted across {len(rules_by_category)} categories."
    )


def _update_session(
    db: DBSession,
    session: SessionModel,
    status: str = None,
    progress: int = None,
    message: str = None,
) -> None:
    if status is not None:
        session.status = status
    if progress is not None:
        session.extraction_progress = progress
    if message is not None:
        session.extraction_message = message
    session.updated_at = _now()
    db.commit()


def _mark_file(
    db: DBSession,
    uploaded_file: UploadedFile,
    status: str,
    error: str = None,
) -> None:
    uploaded_file.status = status
    if error:
        uploaded_file.error_message = error
    db.commit()
