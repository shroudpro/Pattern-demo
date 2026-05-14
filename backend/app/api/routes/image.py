from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schema.generation import ImageGenerationJobCreateRequest, ImageGenerationJobResponse
from app.service.image_generation_service import (
    create_image_generation_job,
    get_image_generation_job_detail,
    process_image_generation_job,
)

router = APIRouter(prefix="/api/v1/image-generation-jobs", tags=["image-generation"])


@router.post("", response_model=ImageGenerationJobResponse)
def post_generate_image_job(
    payload: ImageGenerationJobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = create_image_generation_job(
        db=db,
        analysis_session_id=payload.analysisSessionId,
        character=payload.character,
        analysis=payload.analysis,
        style_preset=payload.stylePreset,
        ratio_preset=payload.ratioPreset,
        scene_preset=payload.scenePreset,
        user_prompt=payload.userPrompt,
    )
    background_tasks.add_task(process_image_generation_job, job["id"])
    return job


@router.get("/{job_id}", response_model=ImageGenerationJobResponse)
def get_image_job(job_id: int, db: Session = Depends(get_db)):
    job = get_image_generation_job_detail(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="图片任务不存在")

    return job
