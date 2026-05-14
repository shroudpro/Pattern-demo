import json
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.providers.dashscope import DashScopeTextGenerationProvider
from app.repository.records import create_analysis_session, get_analysis_session, get_analysis_session_by_character
from app.schema.analysis import AnalysisSessionResponse, CharacterAnalysisPayload
from app.service.character_validation_service import validate_character

REQUIRED_FIELDS = (
    "character",
    "subtitle",
    "shuowenOriginal",
    "shuowenExplanation",
    "modernMeaning",
    "imageryAnalysis",
    "poems",
    "literaryQuotes",
    "visualMotifs",
    "colorPalette",
    "atmosphereTags",
    "forbiddenElements",
    "layoutPriority",
    "backgroundPromptKeywords",
    "commonImages",
    "classicalPoems",
    "designKeywords",
    "summary",
)

MIN_COUNTS = {
    "commonImages": 3,
    "classicalPoems": 2,
    "designKeywords": 3,
    "poems": 2,
    "literaryQuotes": 8,
    "visualMotifs": 3,
    "colorPalette": 3,
    "atmosphereTags": 3,
    "forbiddenElements": 1,
    "backgroundPromptKeywords": 3,
}

MIN_LENGTHS = {
    "subtitle": 6,
    "shuowenOriginal": 8,
    "shuowenExplanation": 15,
    "modernMeaning": 20,
    "imageryAnalysis": 40,
    "summary": 30,
}


@lru_cache(maxsize=1)
def _load_analysis_dataset() -> dict[str, dict]:
    with settings.mock_character_analysis_path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if settings.s_grade_character_analysis_path.exists():
        with settings.s_grade_character_analysis_path.open("r", encoding="utf-8") as file:
            dataset.update(json.load(file))

    return dataset


def _get_text_provider():
    if settings.text_provider == "dashscope":
        return DashScopeTextGenerationProvider()
    return None


def build_character_analysis_prompt(character: str) -> str:
    schema = {
        "character": character,
        "subtitle": "string",
        "shuowenOriginal": "string",
        "shuowenExplanation": "string",
        "modernMeaning": "string",
        "imageryAnalysis": "string",
        "poems": [
            {
                "line": "string",
                "author": "string",
                "title": "string",
                "explanation": "string",
            }
        ],
        "literaryQuotes": [
            {
                "text": "string",
                "source": "string",
                "keywords": ["string"],
            }
        ],
        "visualMotifs": ["string", "string", "string"],
        "colorPalette": ["string", "string", "string"],
        "atmosphereTags": ["string", "string", "string"],
        "forbiddenElements": ["string"],
        "layoutPriority": {"imagery": "high", "shuowen": "medium", "poems": "medium"},
        "backgroundPromptKeywords": ["string", "string", "string"],
        "commonImages": ["string", "string", "string"],
        "classicalPoems": ["string", "string"],
        "designKeywords": ["string", "string", "string"],
        "summary": "string",
    }
    return (
        "你是“纹生万象”项目第一阶段汉字文化分析模块。\n"
        f"请针对单字“{character}”输出一个严格合法的 JSON 对象。\n"
        "不要输出 Markdown，不要输出代码块，不要输出解释，不要输出前后缀文字。\n"
        "输出必须能被 Python json.loads 直接解析，必须使用标准 JSON 双引号。\n"
        "输出语言为简体中文，整体内容必须适合产品展示，不能写成词典释义式短答。\n"
        "要求：\n"
        "1. 必须包含且只围绕以下字段输出。\n"
        "2. 不允许编造《说文解字》原文；不确定时 shuowenOriginal 返回空字符串，不要硬编。\n"
        "3. poems 必须是对象数组，每条必须包含 line、author、title、explanation。\n"
        "4. literaryQuotes 必须是对象数组，至少 8 条，每条必须包含 text、source、keywords；text 必须是以该字为主要意象的古文、诗词、歌赋名句，source 为书名或作者与篇名，keywords 至少包含目标汉字或关键意象词。\n"
        "5. visualMotifs、colorPalette、atmosphereTags、forbiddenElements、backgroundPromptKeywords 必须是 JSON 数组。\n"
        "6. modernMeaning 至少 20 字，必须是现代语义解释。\n"
        "7. imageryAnalysis 至少 40 字，必须从自然、人格、审美、文化、视觉转译角度展开。\n"
        "8. summary 至少 30 字，必须明确说明该字如何组织成汉字文化解析图。\n"
        "9. commonImages、classicalPoems、designKeywords 为兼容旧链路字段，也必须输出。\n"
        "10. 不得出现示例、占位、待补充、TODO 等占位词。\n"
        "请严格使用以下 JSON 结构：\n"
        f"{json.dumps(schema, ensure_ascii=False)}"
    )


def _extract_json_object(raw_text: str) -> dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start_index = raw_text.find("{")
        end_index = raw_text.rfind("}")
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            raise
        return json.loads(raw_text[start_index : end_index + 1])


def _validate_generated_analysis(character: str, payload: dict[str, Any]) -> CharacterAnalysisPayload:
    payload = _normalize_analysis_payload(character, payload)
    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing_fields:
        raise ValueError(f"LLM 输出缺少字段：{missing_fields}")

    if payload.get("character") != character:
        raise ValueError(f"LLM 输出字符不匹配：{payload.get('character')}")

    for field_name, threshold in MIN_LENGTHS.items():
        value = payload.get(field_name)
        if not isinstance(value, str) or len(value.strip()) < threshold:
            raise ValueError(f"LLM 输出字段长度不足：{field_name}")

    for field_name, threshold in MIN_COUNTS.items():
        value = payload.get(field_name)
        if not isinstance(value, list) or len(value) < threshold or not all(isinstance(item, str) for item in value):
            if field_name == "poems" and isinstance(value, list) and len(value) >= threshold:
                continue
            if field_name == "literaryQuotes" and isinstance(value, list) and len(value) >= threshold:
                continue
            raise ValueError(f"LLM 输出字段数量不足或类型错误：{field_name}")

    return CharacterAnalysisPayload(**payload)


def _normalize_poems(payload: dict[str, Any]) -> list[dict[str, str]]:
    poems = payload.get("poems")
    if isinstance(poems, list) and poems and all(isinstance(item, dict) for item in poems):
        normalized = []
        for item in poems:
            normalized.append(
                {
                    "line": str(item.get("line", "")).strip(),
                    "author": str(item.get("author", "佚名")).strip() or "佚名",
                    "title": str(item.get("title", "出处待考")).strip() or "出处待考",
                    "explanation": str(item.get("explanation", "与该字的文化意象相关。")).strip() or "与该字的文化意象相关。",
                }
            )
        return normalized

    classical_poems = payload.get("classicalPoems", [])
    if not isinstance(classical_poems, list):
        classical_poems = []

    return [
        {
            "line": str(line),
            "author": "佚名",
            "title": "出处待考",
            "explanation": "该诗句与当前汉字的文化意象相关，后续可替换为人工校验版本。",
        }
        for line in classical_poems
        if isinstance(line, str) and line.strip()
    ]


def _normalize_literary_quotes(character: str, payload: dict[str, Any], poems: list[dict[str, str]]) -> list[dict[str, Any]]:
    quotes = payload.get("literaryQuotes")
    normalized: list[dict[str, Any]] = []

    if isinstance(quotes, list):
        for item in quotes:
            if not isinstance(item, dict):
                continue

            text = str(item.get("text", "")).strip()
            source = str(item.get("source", "")).strip()
            keywords = _as_string_list(item.get("keywords"))
            if text and source:
                normalized.append(
                    {
                        "text": text,
                        "source": source,
                        "keywords": keywords or [character],
                    }
                )

    if normalized:
        return normalized

    dataset_payload = _load_analysis_dataset().get(character, {})
    dataset_quotes = dataset_payload.get("literaryQuotes")
    if isinstance(dataset_quotes, list) and len(dataset_quotes) >= 8:
        for item in dataset_quotes:
            if not isinstance(item, dict):
                continue

            text = str(item.get("text", "")).strip()
            source = str(item.get("source", "")).strip()
            keywords = _as_string_list(item.get("keywords"))
            if text and source:
                normalized.append(
                    {
                        "text": text,
                        "source": source,
                        "keywords": keywords or [character],
                    }
                )

        if len(normalized) >= 8:
            return normalized

    return [
        {
            "text": poem["line"],
            "source": f"{poem['author']}《{poem['title']}》",
            "keywords": [character],
        }
        for poem in poems
        if poem.get("line")
    ]


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if isinstance(item, str) and item.strip()]


def _normalize_analysis_payload(character: str, payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["character"] = character
    normalized["validated"] = True

    poems = _normalize_poems(normalized)
    literary_quotes = _normalize_literary_quotes(character, normalized, poems)
    visual_motifs = _as_string_list(normalized.get("visualMotifs")) or _as_string_list(normalized.get("commonImages"))
    classical_poems = _as_string_list(normalized.get("classicalPoems")) or [poem["line"] for poem in poems]
    design_keywords = _as_string_list(normalized.get("designKeywords")) or _as_string_list(normalized.get("backgroundPromptKeywords")) or visual_motifs
    atmosphere_tags = _as_string_list(normalized.get("atmosphereTags")) or design_keywords[:4]
    color_palette = _as_string_list(normalized.get("colorPalette")) or ["墨黑", "云白", "黛青"]
    forbidden_elements = _as_string_list(normalized.get("forbiddenElements")) or ["可读文字", "英文大字", "现代商业标识"]
    background_keywords = (
        _as_string_list(normalized.get("backgroundPromptKeywords"))
        or visual_motifs
        + atmosphere_tags
        + color_palette
    )

    normalized["subtitle"] = str(normalized.get("subtitle") or "字源、意象、诗意与视觉形态").strip()
    normalized["modernMeaning"] = str(
        normalized.get("modernMeaning")
        or f"{character}的现代语义可从字源解释、文化意象和视觉转译三个层面理解。{normalized.get('summary', '')}"
    ).strip()
    normalized["poems"] = poems
    normalized["literaryQuotes"] = literary_quotes
    normalized["visualMotifs"] = visual_motifs
    normalized["colorPalette"] = color_palette
    normalized["atmosphereTags"] = atmosphere_tags
    normalized["forbiddenElements"] = forbidden_elements
    normalized["layoutPriority"] = normalized.get("layoutPriority") if isinstance(normalized.get("layoutPriority"), dict) else {
        "imagery": "high",
        "shuowen": "medium",
        "poems": "medium",
    }
    normalized["backgroundPromptKeywords"] = background_keywords
    normalized["commonImages"] = _as_string_list(normalized.get("commonImages")) or visual_motifs
    normalized["classicalPoems"] = classical_poems
    normalized["designKeywords"] = design_keywords

    return normalized


def get_mock_analysis_payload_by_character(character: str) -> CharacterAnalysisPayload:
    dataset = _load_analysis_dataset()
    payload = dataset.get(character)
    if not payload:
        raise ValueError(f"未找到「{character}」的本地分析数据。")

    return CharacterAnalysisPayload(**_normalize_analysis_payload(character, payload))


def has_mock_analysis_payload(character: str) -> bool:
    return character in _load_analysis_dataset()


def get_analysis_payload_by_character(character: str) -> CharacterAnalysisPayload:
    analysis, _ = generate_analysis_payload(character)
    return analysis


def generate_analysis_payload(character: str) -> tuple[CharacterAnalysisPayload, dict[str, Any]]:
    if has_mock_analysis_payload(character):
        return get_mock_analysis_payload_by_character(character), {
            "source": "mock",
            "provider": "mock-local-dataset",
            "fallbackUsed": False,
            "errorMessage": None,
        }

    prompt = build_character_analysis_prompt(character)
    provider = _get_text_provider()

    if provider is None:
        raise ValueError(f"字符「{character}」未命中本地分析库，且当前未配置外接文本模型。")

    try:
        provider_result = provider.generate(prompt)
        parsed_payload = _extract_json_object(provider_result["rawText"])
        analysis = _validate_generated_analysis(character, parsed_payload)
        return analysis, {
            "source": "llm",
            "provider": provider_result.get("provider", "dashscope-text"),
            "model": provider_result.get("model"),
            "fallbackUsed": False,
            "errorMessage": None,
            "rawText": provider_result.get("rawText"),
        }
    except Exception as exc:
        if has_mock_analysis_payload(character):
            return get_mock_analysis_payload_by_character(character), {
                "source": "mock",
                "provider": "mock-local-dataset",
                "fallbackUsed": True,
                "errorMessage": str(exc),
            }

        raise ValueError(f"字符「{character}」未命中本地分析库，且外接模型生成失败：{exc}") from exc


def create_analysis_session_record(db: Session, character: str) -> AnalysisSessionResponse:
    validation = validate_character(character)
    if not validation.validated:
        raise ValueError(validation.message)

    # 复用已有的相同汉字的会话
    existing_record = get_analysis_session_by_character(db=db, character=validation.character)
    if existing_record:
        return serialize_analysis_session(existing_record)

    analysis, meta = generate_analysis_payload(validation.character)
    record = create_analysis_session(
        db=db,
        character=validation.character,
        status="completed",
        payload={
            "validated": True,
            "analysis": analysis.model_dump(),
            "analysisSource": meta["source"],
            "analysisProvider": meta["provider"],
            "fallbackUsed": meta["fallbackUsed"],
            "errorMessage": meta.get("errorMessage"),
        },
    )
    return serialize_analysis_session(record)


def get_analysis_session_detail(db: Session, session_id: int) -> AnalysisSessionResponse | None:
    record = get_analysis_session(db=db, session_id=session_id)
    if not record:
        return None

    return serialize_analysis_session(record)


def serialize_analysis_session(record) -> AnalysisSessionResponse:
    payload = json.loads(record.payload) if record.payload else {}
    analysis_payload = payload.get("analysis", {})
    analysis = CharacterAnalysisPayload(**_normalize_analysis_payload(record.character, analysis_payload))

    return AnalysisSessionResponse(
        id=record.id,
        character=record.character,
        validated=payload.get("validated", False),
        status=record.status,
        analysis=analysis,
        createdAt=_to_iso(record.created_at),
        updatedAt=_to_iso(record.updated_at),
    )


def _to_iso(value: datetime | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    return value.isoformat()
