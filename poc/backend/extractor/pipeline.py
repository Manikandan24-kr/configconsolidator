import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from sqlalchemy.orm import Session as DBSession

from pdf_parser import extract_pdf
from extractor.pass1_categorise import categorise_section
from extractor.pass2_extract import extract_rules_for_category
from extractor.dedup import deduplicate_rules
from models import Session as SessionModel, UploadedFile, Rule, _uuid, _now

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/kriyadocs_uploads"))


def run_extraction_pipeline(session_id: str, db: DBSession) -> None:
    """
    Full two-pass extraction pipeline for a session.
    Processes all files, deduplicates across all, persists to DB.
    Resets rule counts (used for initial extraction).
    """
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        return

    _update_session(db, session, status="extracting", progress=0, message="Starting extraction...")

    files = db.query(UploadedFile).filter(UploadedFile.session_id == session_id).all()
    if not files:
        _update_session(db, session, status="review", progress=100, message="No files to process.")
        return

    rules_by_category: dict[str, list[dict]] = {}
    total_files = len(files)

    for file_idx, uploaded_file in enumerate(files):
        _extract_file(db, session, uploaded_file, file_idx, total_files, rules_by_category)

    _dedup_and_save(db, session, session_id, rules_by_category, incremental=False)


def run_incremental_pipeline(session_id: str, new_file_ids: list[str], db: DBSession) -> None:
    """
    Incremental extraction: only processes the specified new files.
    Merges extracted rules with existing ones, deduplicating per category.
    Preserves confirmed/excluded status on existing rules.
    """
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        return

    _update_session(db, session, status="extracting", progress=0, message="Starting extraction of new files...")

    new_files = db.query(UploadedFile).filter(
        UploadedFile.session_id == session_id,
        UploadedFile.id.in_(new_file_ids),
    ).all()

    if not new_files:
        _update_session(db, session, status="review", progress=100, message="No new files to process.")
        return

    # Extract from new files only
    rules_by_category: dict[str, list[dict]] = {}
    total_files = len(new_files)

    for file_idx, uploaded_file in enumerate(new_files):
        _extract_file(db, session, uploaded_file, file_idx, total_files, rules_by_category)

    _dedup_and_save(db, session, session_id, rules_by_category, incremental=True)


def _extract_file(
    db: DBSession,
    session: SessionModel,
    uploaded_file: UploadedFile,
    file_idx: int,
    total_files: int,
    rules_by_category: dict,
) -> None:
    filepath = Path(uploaded_file.filepath)
    if not filepath.exists():
        _mark_file(db, uploaded_file, "failed", "File not found on disk")
        return

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
        return

    sections = doc.sections if doc.sections else []
    if not sections and doc.raw_text and doc.raw_text.strip():
        sections = [type("S", (), {"title": doc.title, "content": doc.raw_text})()]

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

        categories = categorise_section(content)
        if not categories:
            continue

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


def _dedup_and_save(
    db: DBSession,
    session: SessionModel,
    session_id: str,
    rules_by_category: dict,
    incremental: bool,
) -> None:
    _update_session(db, session, progress=92, message="Deduplicating rules...")

    if incremental:
        # Load existing extracted rules per category, merge with new, dedup together
        existing_rules = db.query(Rule).filter(
            Rule.session_id == session_id,
            Rule.is_custom == False,
        ).all()

        existing_by_cat: dict[str, list[dict]] = {}
        for r in existing_rules:
            existing_by_cat.setdefault(r.category, []).append({
                "rule": r.rule,
                "source_document": r.source_document or "",
                "source_section": r.source_section or "",
                "remarks": r.remarks,
                "_db_id": r.id,
                "_status": r.status,
            })

        # Merge new into existing per category, then dedup
        merged_by_cat: dict[str, list[dict]] = {}
        all_categories = set(list(existing_by_cat.keys()) + list(rules_by_category.keys()))

        for cat in all_categories:
            combined = existing_by_cat.get(cat, []) + rules_by_category.get(cat, [])
            merged_by_cat[cat] = deduplicate_rules(combined)

        # Delete old extracted rules and re-insert merged set
        db.query(Rule).filter(
            Rule.session_id == session_id,
            Rule.is_custom == False,
        ).delete(synchronize_session=False)

        _update_session(db, session, progress=95, message="Saving merged rules to database...")
        total_saved = 0
        for category, rule_list in merged_by_cat.items():
            for order, item in enumerate(rule_list):
                # Preserve confirmed/excluded status if this rule existed before
                status = item.get("_status", "pending")
                rule = Rule(
                    id=_uuid(),
                    session_id=session_id,
                    category=category,
                    rule=item["rule"],
                    source_document=item.get("source_document", ""),
                    source_section=item.get("source_section", ""),
                    remarks=item.get("remarks"),
                    status=status,
                    is_custom=False,
                    sort_order=order,
                    created_at=_now(),
                    updated_at=_now(),
                )
                db.add(rule)
                total_saved += 1

        # Keep custom rules count in total
        custom_count = db.query(Rule).filter(
            Rule.session_id == session_id,
            Rule.is_custom == True,
        ).count()
        total_saved += custom_count

    else:
        # Full extraction: dedup per category then save
        deduped: dict[str, list[dict]] = {}
        for cat, rules in rules_by_category.items():
            deduped[cat] = deduplicate_rules(rules)

        _update_session(db, session, progress=95, message="Saving rules to database...")
        total_saved = 0
        for category, rule_list in deduped.items():
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

    # Recalculate session counts
    all_rules = db.query(Rule).filter(Rule.session_id == session_id).all()
    session.total_rules = len(all_rules)
    session.confirmed_rules = sum(1 for r in all_rules if r.status == "confirmed")
    session.excluded_rules = sum(1 for r in all_rules if r.status == "excluded")
    db.commit()

    new_count = len(rules_by_category)
    _update_session(
        db, session,
        status="review",
        progress=100,
        message=f"{'Merged' if incremental else 'Extraction complete'}. {session.total_rules} rules across {new_count} categories."
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
