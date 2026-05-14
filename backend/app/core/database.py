from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

DATABASE_URL = f"sqlite:///{settings.sqlite_path.as_posix()}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
TIMESTAMP_TABLES = ("generation_history", "project_snapshots", "export_records", "llm_jobs", "image_jobs", "analysis_sessions", "design_projects")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        for table_name in TIMESTAMP_TABLES:
            if table_name not in existing_tables:
                continue

            columns = {column["name"] for column in inspector.get_columns(table_name)}
            if "updated_at" not in columns:
                connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN updated_at DATETIME"))
                connection.execute(text(f"UPDATE {table_name} SET updated_at = created_at WHERE updated_at IS NULL"))
