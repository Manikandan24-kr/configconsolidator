import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from database import Base

VALID_CATEGORIES = [
    "abstract", "acronyms", "capitalization", "hyphenation", "numbers",
    "punctuation", "references", "spelling", "statistical_terms",
    "trademarks", "units", "figures", "general_style",
]

VALID_RULE_STATUSES = ["pending", "confirmed", "excluded"]
VALID_SESSION_STATUSES = ["pending", "uploading", "extracting", "review", "completed"]


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    sessions = relationship("Session", back_populates="customer", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=_uuid)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="pending")       # pending|uploading|extracting|review|completed
    total_pdfs = Column(Integer, default=0)
    total_rules = Column(Integer, default=0)
    confirmed_rules = Column(Integer, default=0)
    excluded_rules = Column(Integer, default=0)
    extraction_progress = Column(Integer, default=0) # 0-100
    extraction_message = Column(Text, default="")
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    customer = relationship("Customer", back_populates="sessions")
    files = relationship("UploadedFile", back_populates="session", cascade="all, delete-orphan")
    rules = relationship("Rule", back_populates="session", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="session", cascade="all, delete-orphan")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending|processing|done|failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)

    session = relationship("Session", back_populates="files")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    category = Column(String, nullable=False)
    rule = Column(Text, nullable=False)
    source_document = Column(String, default="")
    source_section = Column(String, default="")
    remarks = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending|confirmed|excluded
    is_custom = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    session = relationship("Session", back_populates="rules")
    audit_logs = relationship("AuditLog", back_populates="rule", cascade="all, delete-orphan")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    rule_id = Column(String, ForeignKey("rules.id"), nullable=True)
    action = Column(String, nullable=False)  # confirmed|excluded|edited|added|reset|bulk_confirmed|bulk_excluded
    old_value = Column(Text, nullable=True)  # JSON string
    new_value = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=_now)

    session = relationship("Session", back_populates="audit_logs")
    rule = relationship("Rule", back_populates="audit_logs")
