import os
import time
import json
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api-inference.modelscope.cn/"
API_KEY = os.getenv("MODELSCOPE_API_KEY")

if not API_KEY:
    raise ValueError("缺少 MODELSCOPE_API_KEY，请先在 .env 中配置。")

COMMON_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "dunhuang_texture_test.jpg"

# 这个 prompt（提示词）故意只做“敦煌纹理/背景”，不做复杂主体，
# 因为你们现在更适合先测试“辅助素材生成”链路，而不是直接生成最终成品图。
PROMPT = (
    "Create a square decorative texture inspired by Dunhuang mural art. "
    "Use an elegant non-figurative pattern style with lotus motifs, flowing clouds, "
    "subtle mural cracks, mineral pigments, and a refined cultural atmosphere. "
    "Main colors: ochre red, stone green, stone blue, dark brown, with very subtle gold accents. "
    "Flat decorative texture, suitable as a background pattern for a cultural design system. "
    "No text, no people, no animals, no modern objects, no watermark."
)

# 先尝试“低质量 + 小尺寸”参数。
# 如果接口不接受这些可选字段，脚本会自动回退到最小 payload。
PAYLOAD_CANDIDATES = [
    {
        "model": "Qwen/Qwen-Image",
        "prompt": PROMPT,
        "size": "768x768",
        "quality": "low"
    },
    {
        "model": "Qwen/Qwen-Image",
        "prompt": PROMPT
    }
]

def create_task(payload: dict) -> str:
    response = requests.post(
        f"{BASE_URL}v1/images/generations",
        headers={**COMMON_HEADERS, "X-ModelScope-Async-Mode": "true"},
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=60
    )

    # 如果字段非法，比如 quality/size 不支持，就抛异常给外层 fallback
    response.raise_for_status()
    data = response.json()

    if "task_id" not in data:
        raise RuntimeError(f"创建任务失败，响应内容异常：{data}")

    return data["task_id"]

def poll_task(task_id: str, max_wait_seconds: int = 180, interval: int = 5) -> str:
    start = time.time()

    while True:
        result = requests.get(
            f"{BASE_URL}v1/tasks/{task_id}",
            headers={**COMMON_HEADERS, "X-ModelScope-Task-Type": "image_generation"},
            timeout=60
        )
        result.raise_for_status()
        data = result.json()

        status = data.get("task_status")
        print(f"[poll] task_status = {status}")

        if status == "SUCCEED":
            output_images = data.get("output_images", [])
            if not output_images:
                raise RuntimeError(f"任务成功但没有 output_images：{data}")
            return output_images[0]

        if status == "FAILED":
            raise RuntimeError(f"图片生成失败：{data}")

        if time.time() - start > max_wait_seconds:
            raise TimeoutError(f"轮询超时，最后响应：{data}")

        time.sleep(interval)

def download_image(image_url: str, save_path: Path):
    image_resp = requests.get(image_url, timeout=120)
    image_resp.raise_for_status()
    image = Image.open(BytesIO(image_resp.content))
    image.save(save_path)
    print(f"图片已保存到：{save_path.resolve()}")

def main():
    last_error = None
    task_id = None

    for idx, payload in enumerate(PAYLOAD_CANDIDATES, start=1):
        try:
            print(f"\n[try {idx}] 使用 payload: {payload}")
            task_id = create_task(payload)
            print(f"任务创建成功，task_id = {task_id}")
            break
        except Exception as e:
            last_error = e
            print(f"[try {idx}] 创建任务失败：{e}")

    if not task_id:
        raise RuntimeError(f"所有 payload 都失败了，最后错误：{last_error}")

    image_url = poll_task(task_id)
    print(f"图片地址：{image_url}")
    download_image(image_url, OUTPUT_PATH)

if __name__ == "__main__":
    main()