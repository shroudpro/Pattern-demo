import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.providers.dashscope_image import (
    DashScopeImageGenerationProvider,
    get_dashscope_error_detail,
    get_dashscope_result_url,
    get_dashscope_task_id,
    get_dashscope_task_status,
)
from app.providers.image_api import HttpImageGenerationProvider
from app.providers.mock import MockImageGenerationProvider
from app.repository.records import create_image_job, get_image_job, update_image_job
from app.schema.analysis import CharacterAnalysisPayload
from app.service.prompt_composer_service import compose_prompt


def _get_image_provider():
    if settings.image_provider == "dashscope":
        return DashScopeImageGenerationProvider()
    if settings.image_provider == "http":
        return HttpImageGenerationProvider()

    return MockImageGenerationProvider()


def create_image_generation_job(
    db: Session,
    analysis_session_id: int,
    character: str,
    analysis: CharacterAnalysisPayload,
    style_preset: str,
    ratio_preset: str = "16:9",
    scene_preset: str | None = None,
    user_prompt: str | None = None,
) -> dict:
    legacy_scene_preset = scene_preset or ("package" if ratio_preset == "1:1" else "poster")
    prompt = compose_prompt(
        character=character,
        analysis=analysis.model_dump(),
        style_preset=style_preset,
        ratio_preset=ratio_preset,
        scene_preset=legacy_scene_preset,
        user_prompt=user_prompt,
    )
    payload = {
        "analysisSessionId": analysis_session_id,
        "character": character,
        "analysis": analysis.model_dump(),
        "stylePreset": style_preset,
        "ratioPreset": ratio_preset,
        "scenePreset": legacy_scene_preset,
        "positivePrompt": prompt.positivePrompt,
        "userPrompt": user_prompt,
        "negativePrompt": prompt.negativePrompt,
        "width": prompt.width,
        "height": prompt.height,
        "outputUrl": None,
        "localPath": None,
        "errorMessage": None,
        "remoteTaskId": None,
        "remoteTaskStatus": None,
    }
    record = create_image_job(db=db, status="pending", payload=payload)
    return serialize_image_job(record)


def get_image_generation_job_detail(db: Session, job_id: int) -> dict | None:
    record = get_image_job(db=db, job_id=job_id)
    if not record:
        return None

    return serialize_image_job(record)


def process_image_generation_job(job_id: int) -> None:
    with SessionLocal() as db:
        record = get_image_job(db=db, job_id=job_id)
        if not record:
            return

        base_payload = json.loads(record.payload) if record.payload else {}
        size = f"{base_payload['width']}x{base_payload['height']}"
        provider = _get_image_provider()

        try:
            if isinstance(provider, DashScopeImageGenerationProvider):
                _process_dashscope_generation_job(
                    db=db,
                    job_id=job_id,
                    provider=provider,
                    base_payload=base_payload,
                    size=size,
                )
                return

            update_image_job(
                db=db,
                job_id=job_id,
                status="queued",
                payload={"submittedPrompt": base_payload["positivePrompt"]},
            )
            update_image_job(db=db, job_id=job_id, status="generating")
            generated = provider.generate_texture(
                prompt=base_payload["positivePrompt"],
                size=size,
                style_preset=base_payload["stylePreset"],
                scene_preset=base_payload["scenePreset"],
            )
            output_url, local_path = persist_generated_image(
                job_id=job_id,
                character=base_payload["character"],
                generated=generated,
            )
            update_image_job(
                db=db,
                job_id=job_id,
                status="succeeded",
                payload={
                    "outputUrl": output_url,
                    "localPath": local_path,
                    "errorMessage": None,
                },
            )
        except Exception as exc:
            fallback = _resolve_fallback_generated_image(base_payload)
            if fallback:
                update_image_job(
                    db=db,
                    job_id=job_id,
                    status="succeeded",
                    payload={
                        "outputUrl": fallback["outputUrl"],
                        "localPath": fallback["localPath"],
                        "errorMessage": f"图片生成失败，已使用本地解析图模板降级：{exc}",
                        "fallbackUsed": True,
                    },
                )
                return

            update_image_job(
                db=db,
                job_id=job_id,
                status="failed",
                payload={"errorMessage": str(exc), "fallbackUsed": False},
            )


def _process_dashscope_generation_job(
    db: Session,
    job_id: int,
    provider: DashScopeImageGenerationProvider,
    base_payload: dict,
    size: str,
) -> None:
    create_response = provider.create_task(prompt=base_payload["positivePrompt"], size=size)
    task_id = get_dashscope_task_id(create_response)
    update_image_job(
        db=db,
        job_id=job_id,
        status="queued",
        payload={
            "submittedPrompt": base_payload["positivePrompt"],
            "remoteTaskId": task_id,
            "remoteTaskStatus": get_dashscope_task_status(create_response),
            "errorMessage": None,
        },
    )

    for _ in range(24):
        task_response = provider.get_task(task_id)
        task_status = get_dashscope_task_status(task_response)
        if task_status == "SUCCEEDED":
            image_url = get_dashscope_result_url(task_response)
            output_url, local_path = persist_generated_image(
                job_id=job_id,
                character=base_payload["character"],
                generated={
                    "provider": "dashscope-image",
                    "imageUrl": image_url,
                    "remoteTaskId": task_id,
                    "remoteTaskStatus": task_status,
                },
            )
            update_image_job(
                db=db,
                job_id=job_id,
                status="succeeded",
                payload={
                    "outputUrl": output_url,
                    "localPath": local_path,
                    "errorMessage": None,
                    "remoteTaskId": task_id,
                    "remoteTaskStatus": task_status,
                },
            )
            return

        if task_status in {"FAILED", "CANCELED"}:
            error_code, error_message = get_dashscope_error_detail(task_response)
            update_image_job(
                db=db,
                job_id=job_id,
                status="failed",
                payload={
                    "remoteTaskId": task_id,
                    "remoteTaskStatus": task_status,
                },
            )
            detail_parts = [f"task_status={task_status}"]
            if error_code:
                detail_parts.append(f"code={error_code}")
            if error_message:
                detail_parts.append(f"message={error_message}")
            raise RuntimeError(f"DashScope 图片任务失败，{'，'.join(detail_parts)}")

        next_status = "generating" if task_status == "RUNNING" else "queued"
        update_image_job(
            db=db,
            job_id=job_id,
            status=next_status,
            payload={
                "remoteTaskId": task_id,
                "remoteTaskStatus": task_status,
            },
        )
        time.sleep(5)

    raise RuntimeError("DashScope 图片任务轮询超时，未在预期时间内完成。")


def persist_generated_image(job_id: int, character: str, generated: dict) -> tuple[str, str]:
    if generated.get("outputUrl") and generated.get("localPath"):
        return generated["outputUrl"], generated["localPath"]

    root = settings.public_generated_textures_root
    root.mkdir(parents=True, exist_ok=True)

    extension = generated.get("fileExtension")
    if not extension:
        extension = "svg" if generated.get("svgContent") else "png"

    file_name = f"{character}-{job_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.{extension}"
    target_path = root / file_name

    if generated.get("svgContent"):
        target_path.write_text(generated["svgContent"], encoding="utf-8")
    elif generated.get("imageBytes"):
        target_path.write_bytes(generated["imageBytes"])
    elif generated.get("imageUrl"):
        response = httpx.get(generated["imageUrl"], timeout=settings.image_api_timeout_seconds)
        response.raise_for_status()
        target_path.write_bytes(response.content)
    else:
        raise ValueError("图片生成结果缺少可持久化内容")

    output_url = f"/generated/textures/{file_name}"
    return output_url, str(target_path)


def _resolve_fallback_generated_image(payload_or_style: dict | str) -> dict | None:
    if isinstance(payload_or_style, dict):
        style_preset = payload_or_style.get("stylePreset", "traditional")
        character = payload_or_style.get("character")
        ratio_preset = payload_or_style.get("ratioPreset", "16:9")
        fallback_name = "F1.png" if character == "山" and ratio_preset == "16:9" else ("D1.png" if style_preset == "traditional" else "D2.png")
    else:
        style_preset = payload_or_style
        fallback_name = "D1.png" if style_preset == "traditional" else "D2.png"
    fallback_path = settings.project_root / "public" / "img" / fallback_name
    if not fallback_path.exists():
        return None

    return {
        "outputUrl": f"/img/{fallback_name}",
        "localPath": str(fallback_path),
    }


def serialize_image_job(record) -> dict:
    payload = json.loads(record.payload) if record.payload else {}
    return {
        "id": record.id,
        "analysisSessionId": payload.get("analysisSessionId"),
        "character": payload.get("character"),
        "stylePreset": payload.get("stylePreset"),
        "ratioPreset": payload.get("ratioPreset", "16:9"),
        "scenePreset": payload.get("scenePreset"),
        "positivePrompt": payload.get("positivePrompt"),
        "negativePrompt": payload.get("negativePrompt"),
        "width": payload.get("width"),
        "height": payload.get("height"),
        "status": record.status,
        "outputUrl": payload.get("outputUrl"),
        "localPath": payload.get("localPath"),
        "errorMessage": payload.get("errorMessage"),
        "fallbackUsed": payload.get("fallbackUsed", False),
        "createdAt": record.created_at.isoformat(),
    }
