from app.providers.base import EmbeddingProvider, ImageGenerationProvider, TextGenerationProvider
from app.core.config import settings


class MockTextGenerationProvider(TextGenerationProvider):
    def generate(self, prompt: str) -> dict:
        return {"provider": "mock-text", "prompt": prompt, "status": "mocked"}

    def enhance_entry(self, prompt: str) -> dict:
        return {
            "provider": "mock-text",
            "recommendReasonEnhanced": "当前使用 mock 文本增强，保留原始推荐理由结构并做轻量润色。",
            "imageryTagsCandidates": ["纹样意象", "文化语义"],
            "moodTagsCandidates": ["稳定", "清晰"],
        }

    def enhance_render_plan(self, prompt: str) -> dict:
        return {
            "provider": "mock-text",
            "shortCaptionEnhanced": "当前使用 mock 增强说明，用于占位文本润色。",
            "explanationSummary": "当前模板与渲染计划的关系由规则引擎决定，LLM 只参与说明文案增强。",
        }


class MockImageGenerationProvider(ImageGenerationProvider):
    def generate(self, prompt: str) -> dict:
        return {"provider": "mock-image", "prompt": prompt, "status": "mocked"}

    def generate_texture(self, prompt: str, size: str, style_preset: str, scene_preset: str) -> dict:
        if "Character: 山" in prompt and "16:9" in prompt:
            local_path = settings.project_root / "public" / "img" / "F1.png"
            return {
                "provider": "mock-image",
                "status": "mocked",
                "mimeType": "image/png",
                "fileExtension": "png",
                "outputUrl": "/img/F1.png",
                "localPath": str(local_path),
            }

        file_name = f"{scene_preset}-{style_preset}.png"
        local_path = settings.public_mock_textures_root / file_name
        output_url = f"/mock/textures/{file_name}"
        if not local_path.exists():
            fallback_name = "D1.png" if style_preset == "traditional" else "D2.png"
            local_path = settings.project_root / "public" / "img" / fallback_name
            output_url = f"/img/{fallback_name}"
        if not local_path.exists():
            raise FileNotFoundError(f"未找到 mock 解析图背景: {local_path}")
        return {
            "provider": "mock-image",
            "status": "mocked",
            "mimeType": "image/png",
            "fileExtension": "png",
            "outputUrl": output_url,
            "localPath": str(local_path),
        }


class MockEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> dict:
        return {"provider": "mock-embedding", "text": text, "vector": [0.0, 0.1, 0.2]}
