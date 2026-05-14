import base64
from typing import Any

import httpx

from app.core.config import settings


class HttpImageGenerationProvider:
    """
    使用可配置的 OpenAI 兼容图片接口生成纹理图。
    这里不参与规则决策，只返回辅助纹理原始结果。
    """

    def generate(self, prompt: str) -> dict:
        return self.generate_texture(prompt=prompt, size="1024x1024", style_preset="traditional", scene_preset="package")

    def generate_texture(self, prompt: str, size: str, style_preset: str, scene_preset: str) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if settings.image_api_key:
            headers["Authorization"] = f"Bearer {settings.image_api_key}"

        response = httpx.post(
            f"{settings.image_api_base_url}/images/generations",
            json={
                "model": settings.image_api_model_name,
                "prompt": prompt,
                "size": size,
                "response_format": "b64_json",
            },
            headers=headers,
            timeout=settings.image_api_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])
        if not data:
            raise ValueError("图片接口未返回 data")

        first_item = data[0]
        b64_json = first_item.get("b64_json")
        if b64_json:
            return {
                "provider": "http-image",
                "mimeType": "image/png",
                "fileExtension": "png",
                "imageBytes": base64.b64decode(b64_json),
            }

        image_url = first_item.get("url")
        if image_url:
            return {
                "provider": "http-image",
                "imageUrl": image_url,
            }

        raise ValueError("图片接口返回缺少 b64_json 或 url")
