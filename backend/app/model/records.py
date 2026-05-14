from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class GenerationHistory(TimestampMixin, Base):
    __tablename__ = "generation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entry_id: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[str] = mapped_column(Text)


class ProjectSnapshot(TimestampMixin, Base):
    __tablename__ = "project_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    payload: Mapped[str] = mapped_column(Text)


class ExportRecord(TimestampMixin, Base):
    __tablename__ = "export_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mode: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    payload: Mapped[str] = mapped_column(Text)


class LLMJob(TimestampMixin, Base):
    __tablename__ = "llm_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(32))
    payload: Mapped[str] = mapped_column(Text)


class ImageJob(TimestampMixin, Base):
    __tablename__ = "image_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(32))
    payload: Mapped[str] = mapped_column(Text)


class AnalysisSession(TimestampMixin, Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    character: Mapped[str] = mapped_column(String(16), index=True)
    status: Mapped[str] = mapped_column(String(32))
    payload: Mapped[str] = mapped_column(Text)


class DesignProject(TimestampMixin, Base):
    __tablename__ = "design_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    character: Mapped[str] = mapped_column(String(16), index=True)
    analysis_session_id: Mapped[int] = mapped_column(Integer, index=True)
    image_job_id: Mapped[int] = mapped_column(Integer, index=True)
    payload: Mapped[str] = mapped_column(Text)
