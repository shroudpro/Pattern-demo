import json

from sqlalchemy.orm import Session

from app.model.records import AnalysisSession, DesignProject, ExportRecord, GenerationHistory, ImageJob


def create_generation_history(db: Session, entry_id: str, payload: dict) -> GenerationHistory:
    record = GenerationHistory(entry_id=entry_id, payload=json.dumps(payload, ensure_ascii=False))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def create_export_record(db: Session, mode: str, status: str, payload: dict) -> ExportRecord:
    record = ExportRecord(mode=mode, status=status, payload=json.dumps(payload, ensure_ascii=False))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def create_image_job(db: Session, status: str, payload: dict) -> ImageJob:
    record = ImageJob(status=status, payload=json.dumps(payload, ensure_ascii=False))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def create_analysis_session(db: Session, character: str, status: str, payload: dict) -> AnalysisSession:
    record = AnalysisSession(character=character, status=status, payload=json.dumps(payload, ensure_ascii=False))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_analysis_session(db: Session, session_id: int) -> AnalysisSession | None:
    return db.get(AnalysisSession, session_id)


def get_analysis_session_by_character(db: Session, character: str) -> AnalysisSession | None:
    return db.query(AnalysisSession).filter(
        AnalysisSession.character == character, 
        AnalysisSession.status == "completed"
    ).order_by(AnalysisSession.id.desc()).first()


def get_image_job(db: Session, job_id: int) -> ImageJob | None:
    return db.get(ImageJob, job_id)


def create_project_record(
    db: Session,
    character: str,
    analysis_session_id: int,
    image_job_id: int,
    payload: dict,
) -> DesignProject:
    record = DesignProject(
        character=character,
        analysis_session_id=analysis_session_id,
        image_job_id=image_job_id,
        payload=json.dumps(payload, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_project_record(db: Session, project_id: int) -> DesignProject | None:
    return db.get(DesignProject, project_id)


def update_project_record(db: Session, project_id: int, payload: dict) -> DesignProject | None:
    record = get_project_record(db=db, project_id=project_id)
    if not record:
        return None

    current_payload = json.loads(record.payload) if record.payload else {}
    current_payload.update(payload)
    record.payload = json.dumps(current_payload, ensure_ascii=False)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_image_job(db: Session, job_id: int, status: str | None = None, payload: dict | None = None) -> ImageJob | None:
    record = get_image_job(db=db, job_id=job_id)
    if not record:
        return None

    current_payload = json.loads(record.payload) if record.payload else {}
    if payload:
        current_payload.update(payload)

    if status:
        record.status = status

    record.payload = json.dumps(current_payload, ensure_ascii=False)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
