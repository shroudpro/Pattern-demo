import json

import httpx

from app.core.config import settings


class OllamaTextGenerationProvider:
    def _generate_json(self, prompt: str) -> dict:
        response = httpx.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=settings.ollama_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload.get("response", "{}")
        return json.loads(content)

    def enhance_entry(self, prompt: str) -> dict:
        return self._generate_json(prompt)

    def enhance_render_plan(self, prompt: str) -> dict:
        return self._generate_json(prompt)
