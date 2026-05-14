from typing import Literal

from pydantic import BaseModel


class CharacterValidationRequest(BaseModel):
    character: str


class CharacterValidationResult(BaseModel):
    character: str
    validated: bool
    message: str


class PoemPayload(BaseModel):
    line: str
    author: str
    title: str
    explanation: str


class LiteraryQuotePayload(BaseModel):
    text: str
    source: str
    keywords: list[str]


class CharacterAnalysisPayload(BaseModel):
    character: str
    validated: bool
    subtitle: str
    shuowenOriginal: str
    shuowenExplanation: str
    modernMeaning: str
    imageryAnalysis: str
    poems: list[PoemPayload]
    literaryQuotes: list[LiteraryQuotePayload]
    visualMotifs: list[str]
    colorPalette: list[str]
    atmosphereTags: list[str]
    forbiddenElements: list[str]
    layoutPriority: dict[str, str]
    backgroundPromptKeywords: list[str]
    commonImages: list[str]
    classicalPoems: list[str]
    designKeywords: list[str]
    summary: str


class AnalysisSessionResponse(BaseModel):
    id: int
    character: str
    validated: bool
    status: Literal["completed"]
    analysis: CharacterAnalysisPayload
    createdAt: str
    updatedAt: str


class PromptComposeRequest(BaseModel):
    character: str
    analysis: CharacterAnalysisPayload
    stylePreset: Literal["traditional", "modern"]
    ratioPreset: Literal["16:9", "1:1", "9:16"] = "16:9"
    scenePreset: Literal["poster", "package"] | None = None


class PromptComposeResult(BaseModel):
    positivePrompt: str
    negativePrompt: str
    width: int
    height: int
    stylePreset: Literal["traditional", "modern"]
    ratioPreset: Literal["16:9", "1:1", "9:16"]
    scenePreset: Literal["poster", "package"] | None = None
