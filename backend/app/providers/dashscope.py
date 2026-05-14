import json
import urllib.error
import urllib.request

from app.core.config import settings


class DashScopeTextGenerationProvider:
    """
    使用 DashScope OpenAI 兼容 responses 接口生成文本。
    """

    def generate(self, prompt: str) -> dict:
        if not settings.dashscope_api_key:
            raise RuntimeError("DASHSCOPE_API_KEY 未配置，无法调用外接文本模型。")

        request = urllib.request.Request(
            f"{settings.dashscope_base_url.rstrip('/')}/responses",
            data=json.dumps(
                {
                    "model": settings.dashscope_model_name,
                    "input": prompt,
                    "extra_body": {
                        "enable_thinking": False,
                    },
                },
                ensure_ascii=False,
            ).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.dashscope_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=settings.dashscope_timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DashScope 请求失败: HTTP {exc.code} - {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DashScope 网络错误：{exc}") from exc

        response_json = json.loads(response_body)
        raw_text = self._extract_text(response_json)
        if not raw_text:
            raise RuntimeError(f"DashScope 返回成功但未解析到文本，原始响应：{json.dumps(response_json, ensure_ascii=False)}")

        return {
            "provider": "dashscope-text",
            "model": settings.dashscope_model_name,
            "rawText": raw_text,
            "rawResponse": response_json,
        }

    def _extract_text(self, response_json: dict) -> str:
        output = response_json.get("output") or []
        texts: list[str] = []

        for item in output:
            for content in item.get("content") or []:
                text = content.get("text")
                if text:
                    texts.append(text)

        return "\n".join(texts).strip()
