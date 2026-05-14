import json
import urllib.error
import urllib.request
from typing import Any

from app.core.config import settings


def format_dashscope_size(size: str) -> str:
    """
    把项目内部的 864x1152 转成 DashScope 要求的 864*1152。
    """

    width, height = parse_internal_size(size)
    width = normalize_to_multiple_of_8(width)
    height = normalize_to_multiple_of_8(height)
    return f"{width}*{height}"


def parse_internal_size(size: str) -> tuple[int, int]:
    try:
        width_text, height_text = size.lower().split("x", maxsplit=1)
        return int(width_text), int(height_text)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"非法 DashScope 图片尺寸：{size}") from exc


def normalize_to_multiple_of_8(value: int) -> int:
    if value < 8:
        raise ValueError(f"DashScope 图片尺寸过小：{value}")
    return value - (value % 8)


def get_dashscope_task_status(payload: dict[str, Any]) -> str | None:
    return payload.get("output", {}).get("task_status")


def get_dashscope_task_id(payload: dict[str, Any]) -> str:
    task_id = payload.get("output", {}).get("task_id")
    if not task_id:
        raise ValueError(f"DashScope 创建任务成功，但响应中没有 task_id：{json.dumps(payload, ensure_ascii=False)}")
    return str(task_id)


def get_dashscope_result_url(payload: dict[str, Any]) -> str:
    results = payload.get("output", {}).get("results") or []
    if not results or not results[0].get("url"):
        raise ValueError(f"DashScope 任务成功，但响应中没有图片 URL：{json.dumps(payload, ensure_ascii=False)}")
    return str(results[0]["url"])


def get_dashscope_error_detail(payload: dict[str, Any]) -> tuple[str | None, str | None]:
    output = payload.get("output", {})
    return output.get("code"), output.get("message")


class DashScopeImageGenerationProvider:
    """
    使用 DashScope 异步文生图接口生成纹理图。
    """

    def _build_headers(self, extra_headers: dict[str, str] | None = None) -> dict[str, str]:
        if not settings.dashscope_api_key:
            raise RuntimeError("DASHSCOPE_API_KEY 未配置，无法调用 DashScope 图片模型。")

        headers = {
            "Authorization": f"Bearer {settings.dashscope_api_key}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def create_task(self, prompt: str, size: str) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{settings.dashscope_image_base_url.rstrip('/')}/services/aigc/text2image/image-synthesis",
            data=json.dumps(
                {
                    "model": settings.dashscope_image_model_name,
                    "input": {"prompt": prompt},
                    "parameters": {
                        "size": format_dashscope_size(size),
                        "n": 1,
                    },
                },
                ensure_ascii=False,
            ).encode("utf-8"),
            headers=self._build_headers({"X-DashScope-Async": "enable"}),
            method="POST",
        )
        return self._send_request(request)

    def get_task(self, task_id: str) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{settings.dashscope_image_base_url.rstrip('/')}/tasks/{task_id}",
            headers=self._build_headers(),
            method="GET",
        )
        return self._send_request(request)

    def generate(self, prompt: str) -> dict:
        return self.generate_texture(prompt=prompt, size="1024x1024", style_preset="traditional", scene_preset="package")

    def generate_texture(self, prompt: str, size: str, style_preset: str, scene_preset: str) -> dict[str, Any]:
        """
        兼容旧接口；在 DashScope provider 中不直接同步返回图片，而是仅用于兜底场景。
        """

        create_payload = self.create_task(prompt=prompt, size=size)
        task_id = get_dashscope_task_id(create_payload)
        task_payload = self.get_task(task_id)
        image_url = get_dashscope_result_url(task_payload)
        return {
            "provider": "dashscope-image",
            "imageUrl": image_url,
            "remoteTaskId": task_id,
            "remoteTaskStatus": get_dashscope_task_status(task_payload),
        }

    def _send_request(self, request: urllib.request.Request) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(request, timeout=settings.dashscope_image_timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DashScope 图片请求失败: HTTP {exc.code} - {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DashScope 图片网络错误：{exc}") from exc
