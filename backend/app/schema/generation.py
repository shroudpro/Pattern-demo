from typing import Literal

from pydantic import BaseModel

from app.schema.analysis import CharacterAnalysisPayload


class ImageGenerationJobCreateRequest(BaseModel):
    analysisSessionId: int
    character: str
    analysis: CharacterAnalysisPayload
    stylePreset: Literal["traditional", "modern"]
    ratioPreset: Literal["16:9", "1:1", "9:16"] = "16:9"
    scenePreset: Literal["poster", "package"] | None = None
    userPrompt: str | None = None


class ImageGenerationJobResponse(BaseModel):
    id: int
    analysisSessionId: int
    character: str
    stylePreset: Literal["traditional", "modern"]
    ratioPreset: Literal["16:9", "1:1", "9:16"]
    scenePreset: Literal["poster", "package"] | None = None
    positivePrompt: str
    negativePrompt: str
    width: int
    height: int
    status: Literal["pending", "queued", "generating", "succeeded", "failed"]
    outputUrl: str | None = None
    localPath: str | None = None
    errorMessage: str | None = None
    fallbackUsed: bool = False
    createdAt: str
