TEXTURE_TYPE_LABELS = {
    "dunhuang_texture": "敦煌纹理",
    "qinghua_texture": "青花纹理",
    "miaoxiu_texture": "苗绣纹理",
}


def build_texture_prompt(texture_type: str, size: str, prompt_override: str | None = None) -> str:
    """
    图片生成只负责辅助纹理层，因此提示词严格收敛到材质、装饰和背景纹理语义。
    """

    if prompt_override:
        return prompt_override.strip()

    label = TEXTURE_TYPE_LABELS.get(texture_type, texture_type)
    return (
        f"{label}，用于文化设计系统的辅助背景纹理层，平铺友好，图案连续，"
        f"保留传统工艺气质，避免人物、场景、成品海报，输出尺寸 {size}。"
    )


def build_texture_svg(prompt: str, size: str) -> str:
    width, height = parse_texture_size(size)
    accent = "#8f3647" if "traditional" in prompt else "#2e5a84"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f8f9fa" />
  <g fill="none" stroke="{accent}" stroke-width="4" opacity="0.78">
    <circle cx="{width * 0.25}" cy="{height * 0.28}" r="{min(width, height) * 0.12}" />
    <circle cx="{width * 0.72}" cy="{height * 0.34}" r="{min(width, height) * 0.18}" />
    <path d="M {width * 0.12} {height * 0.76} C {width * 0.28} {height * 0.62}, {width * 0.48} {height * 0.94}, {width * 0.7} {height * 0.72}" />
    <path d="M {width * 0.18} {height * 0.18} L {width * 0.82} {height * 0.82}" opacity="0.28" />
    <path d="M {width * 0.82} {height * 0.18} L {width * 0.18} {height * 0.82}" opacity="0.28" />
    <path d="M {width * 0.08} {height * 0.52} C {width * 0.24} {height * 0.36}, {width * 0.58} {height * 0.62}, {width * 0.9} {height * 0.46}" opacity="0.42" />
  </g>
</svg>"""


def parse_texture_size(size: str) -> tuple[int, int]:
    try:
        width_text, height_text = size.lower().split("x", maxsplit=1)
        return int(width_text), int(height_text)
    except ValueError as exc:
        raise ValueError(f"非法尺寸: {size}") from exc
