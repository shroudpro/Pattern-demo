from sqlalchemy.orm import Session

from app.repository.records import create_project_record, get_project_record, update_project_record


def create_project(
    db: Session,
    character: str,
    analysis_session_id: int,
    image_job_id: int,
    background_image_url: str,
    canvas_width: int,
    canvas_height: int,
    elements: list[dict] | None,
    project_type: str | None = None,
    style_preset: str | None = None,
    ratio_preset: str | None = None,
    layout_spec: dict | None = None,
):
    return create_project_record(
        db=db,
        character=character,
        analysis_session_id=analysis_session_id,
        image_job_id=image_job_id,
        payload={
            "projectType": project_type or "design",
            "backgroundImageUrl": background_image_url,
            "canvasWidth": canvas_width,
            "canvasHeight": canvas_height,
            "stylePreset": style_preset,
            "ratioPreset": ratio_preset,
            "layoutSpec": layout_spec,
            "elements": elements or [],
        },
    )


def get_project(db: Session, project_id: int):
    return get_project_record(db=db, project_id=project_id)


def update_project_elements(
    db: Session,
    project_id: int,
    elements: list[dict],
    layout_spec: dict | None = None,
):
    payload = {"elements": elements}
    if layout_spec is not None:
        payload["layoutSpec"] = layout_spec
    return update_project_record(db=db, project_id=project_id, payload=payload)
