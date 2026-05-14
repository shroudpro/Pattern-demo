import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schema.project import ProjectCreateRequest, ProjectResponse, ProjectUpdateRequest
from app.service.project_editor_service import (
    create_project as create_project_record,
    get_project as get_project_record,
    update_project_elements,
)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
def create_project(payload: ProjectCreateRequest, db: Session = Depends(get_db)):
    record = create_project_record(
        db=db,
        character=payload.character,
        analysis_session_id=payload.analysisSessionId,
        image_job_id=payload.imageJobId,
        background_image_url=payload.backgroundImageUrl,
        canvas_width=payload.canvasWidth,
        canvas_height=payload.canvasHeight,
        elements=payload.elements,
        project_type=payload.projectType,
        style_preset=payload.stylePreset,
        ratio_preset=payload.ratioPreset,
        layout_spec=payload.layoutSpec,
    )
    return serialize_project(record)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    record = get_project_record(db=db, project_id=project_id)
    if not record:
        raise HTTPException(status_code=404, detail="设计项目不存在")

    return serialize_project(record)


@router.patch("/{project_id}", response_model=ProjectResponse)
def patch_project(project_id: int, payload: ProjectUpdateRequest, db: Session = Depends(get_db)):
    record = update_project_elements(
        db=db,
        project_id=project_id,
        elements=payload.elements,
        layout_spec=payload.layoutSpec,
    )
    if not record:
        raise HTTPException(status_code=404, detail="设计项目不存在")

    return serialize_project(record)


def serialize_project(record) -> ProjectResponse:
    payload = json.loads(record.payload) if record.payload else {}
    return ProjectResponse(
        id=record.id,
        projectType=payload.get("projectType"),
        character=record.character,
        analysisSessionId=record.analysis_session_id,
        imageJobId=record.image_job_id,
        backgroundImageUrl=payload.get("backgroundImageUrl", ""),
        canvasWidth=payload.get("canvasWidth", 1024),
        canvasHeight=payload.get("canvasHeight", 1024),
        stylePreset=payload.get("stylePreset"),
        ratioPreset=payload.get("ratioPreset"),
        layoutSpec=payload.get("layoutSpec"),
        elements=payload.get("elements", []),
        createdAt=_to_iso(record.created_at),
        updatedAt=_to_iso(record.updated_at),
    )


def _to_iso(value: datetime | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    return value.isoformat()
