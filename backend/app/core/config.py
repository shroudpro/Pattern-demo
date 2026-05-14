import os
from pathlib import Path


def load_env_file() -> None:
    """
    轻量加载项目根目录 .env，避免评测脚本在离线场景下拿不到环境变量。
    """

    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()


def parse_csv_env(value: str | None) -> list[str]:
    if not value:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    """
    后端配置集中在这里，避免路径和命令散落在 service 层。
    """

    project_root: Path = Path(__file__).resolve().parents[3]
    content_root: Path = project_root / "src" / "content" / "config"
    sqlite_path: Path = project_root / "backend" / "wen-sheng-v2.sqlite3"
    npm_command: str = "npm.cmd"
    text_provider: str = os.getenv("WENSHENG_TEXT_PROVIDER", "mock")
    dashscope_base_url: str = os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1",
    )
    dashscope_model_name: str = os.getenv("DASHSCOPE_MODEL_NAME", "qwen3.6-35b-a3b")
    dashscope_api_key: str | None = os.getenv("DASHSCOPE_API_KEY")
    dashscope_timeout_seconds: int = int(os.getenv("DASHSCOPE_TIMEOUT_SECONDS", "60"))
    image_provider: str = os.getenv("WENSHENG_IMAGE_PROVIDER", "mock")
    dashscope_image_base_url: str = os.getenv("DASHSCOPE_IMAGE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
    dashscope_image_model_name: str = os.getenv("DASHSCOPE_IMAGE_MODEL_NAME", "wanx2.0-t2i-turbo")
    dashscope_image_timeout_seconds: int = int(os.getenv("DASHSCOPE_IMAGE_TIMEOUT_SECONDS", "120"))
    image_api_base_url: str = os.getenv("WENSHENG_IMAGE_API_BASE_URL", "http://127.0.0.1:8001")
    image_api_model_name: str = os.getenv("WENSHENG_IMAGE_MODEL_NAME", "gpt-image-1")
    image_api_timeout_seconds: int = int(os.getenv("WENSHENG_IMAGE_TIMEOUT_SECONDS", "120"))
    image_api_key: str | None = os.getenv("WENSHENG_IMAGE_API_KEY")
    cors_allowed_origins: list[str] = parse_csv_env(os.getenv("WENSHENG_CORS_ALLOWED_ORIGINS")) or [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:3001",
        "http://localhost:3001",
    ]
    cors_allow_origin_regex: str | None = os.getenv(
        "WENSHENG_CORS_ALLOW_ORIGIN_REGEX",
        r"^http://(localhost|127\.0\.0\.1):\d+$",
    )
    public_generated_textures_root: Path = project_root / "public" / "generated" / "textures"
    mock_character_analysis_path: Path = project_root / "src" / "lib" / "mock" / "character-analysis.json"
    s_grade_character_analysis_path: Path = project_root / "src" / "lib" / "mock" / "s-grade-character-analysis.json"
    public_mock_textures_root: Path = project_root / "public" / "mock" / "textures"


settings = Settings()
