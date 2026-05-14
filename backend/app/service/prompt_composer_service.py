from app.schema.analysis import PromptComposeResult


CONFLICTING_PROMPT_KEYWORDS = {"no text", "text-free", "without text", "no typography"}


def _clean_prompt_keywords(keywords: list[str]) -> list[str]:
    return [item for item in keywords if item.strip().lower() not in CONFLICTING_PROMPT_KEYWORDS]


def compose_prompt(
    character: str,
    analysis: dict,
    style_preset: str,
    ratio_preset: str = "16:9",
    scene_preset: str | None = None,
    user_prompt: str | None = None,
) -> PromptComposeResult:
    # DashScope image synthesis is strict about dimensions. These sizes keep the
    # intended ratios while staying provider-friendly and divisible by 8.
    ratio_sizes = {
        "16:9": (1280, 720),
        "1:1": (1024, 1024),
        "9:16": (720, 1280),
    }
    width, height = ratio_sizes.get(ratio_preset, ratio_sizes["16:9"])
    visual_motifs = analysis.get("visualMotifs", []) or analysis.get("commonImages", [])
    color_palette = analysis.get("colorPalette", [])
    atmosphere_tags = analysis.get("atmosphereTags", [])
    forbidden_elements = analysis.get("forbiddenElements", [])
    prompt_keywords = _clean_prompt_keywords(analysis.get("backgroundPromptKeywords", []))
    summary = analysis.get("summary", "")
    subtitle = analysis.get("subtitle", "")
    shuowen_original = analysis.get("shuowenOriginal", "")
    shuowen = analysis.get("shuowenExplanation", "")
    modern_meaning = analysis.get("modernMeaning", "")
    poems = analysis.get("poems", [])
    poem_items = [item for item in poems if isinstance(item, dict)][:2]
    poem_lines = "；".join(
        f"{item.get('line', '')} —— {item.get('author', '')}《{item.get('title', '')}》".strip()
        for item in poem_items
        if item.get("line")
    )
    user_prompt_text = (user_prompt or "").strip()

    style_description = (
        "traditional Chinese ink cultural interpretation poster, rice paper texture, restrained dark gold accents, complete editorial layout"
        if style_preset == "traditional"
        else "modern museum Chinese character cultural interpretation poster, subtle grid, low saturation, clean editorial hierarchy"
    )

    positive_prompt = (
        f"Character: {character}. "
        f"Task: create a finished Chinese character cultural interpretation infographic, matching the provided F1 reference style: readable editorial poster, not a calligraphy-only artwork. "
        f"Style preset: {style_preset}. "
        f"Style direction: {style_description}. "
        f"Infographic ratio: {ratio_preset}. "
        f"Required visible Chinese title: {character}：{subtitle}. "
        f"Required left vertical label: 汉字文化 · 意象解析. "
        f"Required central main glyph: one large black brush-style Chinese character “{character}”, placed on the left-center, with small caption 甲骨文 below it. "
        f"Required right-side content panels with dark blue vertical section badges and readable Chinese body text. "
        f"Panel 1 badge text: 说文解字. Panel 1 body text must include exactly: {shuowen_original}. "
        f"Panel 2 badge text: 现代释义. Panel 2 body text must include: {modern_meaning}. "
        f"Panel 3 badge text: 意象分析. Panel 3 must show four small circular motif illustrations and labels from: {', '.join(visual_motifs[:4])}. "
        f"Panel 4 badge text: 常见诗词. Panel 4 body text must include these poem lines: {poem_lines}. "
        f"Cultural summary: {summary}. "
        f"Visual motifs: {', '.join(visual_motifs)}. "
        f"Color palette: {', '.join(color_palette)}. "
        f"Atmosphere: {', '.join(atmosphere_tags)}. "
        f"Prompt keywords: {', '.join(prompt_keywords)}. "
        f"Composition: parchment rice-paper background, ink-wash mountains along the bottom and corners, fine dark-gold decorative lines, seal stamps, clean margins, left large glyph area, right stacked explanation panels, all Chinese text should be readable and arranged as infographic typography, no fake scribbles replacing the required body text. "
        f"User customization requirements: {user_prompt_text if user_prompt_text else 'none'}."
    )
    negative_prompt = (
        "English text, nonsense filler text, unreadable body copy, random decorative scribbles used as text, watermark, QR code, UI screenshot, "
        "unfinished layout, empty placeholder boxes, product mockup, human portrait, calligraphy-only scroll without infographic panels, "
        f"{', '.join(forbidden_elements)}"
    )

    return PromptComposeResult(
        positivePrompt=positive_prompt,
        negativePrompt=negative_prompt,
        width=width,
        height=height,
        stylePreset=style_preset,
        ratioPreset=ratio_preset,
        scenePreset=scene_preset,
    )
