from typing import Any

from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    projectType: str | None = None
    character: str
    analysisSessionId: int
    imageJobId: int
    backgroundImageUrl: str
    canvasWidth: int
    canvasHeight: int
    stylePreset: str | None = None
    ratioPreset: str | None = None
    layoutSpec: dict[str, Any] | None = None
    elements: list[dict[str, Any]] | None = None


class ProjectUpdateRequest(BaseModel):
    elements: list[dict[str, Any]]
    layoutSpec: dict[str, Any] | None = None


class ProjectResponse(BaseModel):
    id: int
    projectType: str | None = None
    character: str
    analysisSessionId: int
    imageJobId: int
    backgroundImageUrl: str
    canvasWidth: int
    canvasHeight: int
    stylePreset: str | None = None
    ratioPreset: str | None = None
    layoutSpec: dict[str, Any] | None = None
    elements: list[dict[str, Any]]
    createdAt: str
    updatedAt: str
