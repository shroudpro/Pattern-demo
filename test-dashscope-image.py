import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Optional


ENV_PATH = Path(__file__).resolve().parent / ".env"
BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
MODEL_NAME = "wanx2.0-t2i-turbo"
OUTPUT_IMAGE_PATH = Path(__file__).resolve().parent / "dashscope-image-test-output.png"


def loadEnvFile(envPath: Path) -> Dict[str, str]:
    """
    只读取根目录 .env，并兼容键值两侧多余空格，避免联调被格式问题干扰。
    """
    values: Dict[str, str] = {}
    if not envPath.exists():
        return values

    for rawLine in envPath.read_text(encoding="utf-8").splitlines():
        line = rawLine.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')

    return values


def getApiKey() -> str:
    """
    优先读取系统环境变量，缺失时回退到根目录 .env。
    """
    envValues = loadEnvFile(ENV_PATH)
    apiKey = os.getenv("DASHSCOPE_API_KEY") or envValues.get("DASHSCOPE_API_KEY")
    if not apiKey:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY，请检查根目录 .env。")
    return apiKey


def sendJsonRequest(url: str, payload: Dict, apiKey: str, headers: Optional[Dict[str, str]] = None) -> Dict:
    """
    统一封装 JSON 请求，确保接口失败时能把原始错误返回到终端。
    """
    requestHeaders = {
        "Authorization": f"Bearer {apiKey}",
        "Content-Type": "application/json",
    }
    if headers:
        requestHeaders.update(headers)

    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=requestHeaders,
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def sendGetRequest(url: str, apiKey: str, headers: Optional[Dict[str, str]] = None) -> Dict:
    """
    轮询异步任务状态时复用相同的鉴权逻辑。
    """
    requestHeaders = {
        "Authorization": f"Bearer {apiKey}",
    }
    if headers:
        requestHeaders.update(headers)

    request = urllib.request.Request(url, headers=requestHeaders, method="GET")
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def downloadFile(url: str, savePath: Path) -> None:
    """
    图片生成成功后直接写入根目录，方便肉眼确认接口链路完整。
    """
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=120) as response:
        savePath.write_bytes(response.read())


def main() -> int:
    """
    发起一次文生图测试，请求成功后把结果图片保存到根目录。
    """
    apiKey = getApiKey()
    prompt = "一间有着精致窗户的花店，漂亮的木质门，门口摆放着新鲜花束，暖色阳光，写实风格，高质量构图"
    createUrl = f"{BASE_URL}/services/aigc/text2image/image-synthesis"

    print("开始测试 DashScope 文生图接口...")
    print(f"base_url: {BASE_URL}")
    print(f"model: {MODEL_NAME}")
    print(f"output: {OUTPUT_IMAGE_PATH}")

    createPayload = {
        "model": MODEL_NAME,
        "input": {
            "prompt": prompt,
        },
        "parameters": {
            "size": "1024*1024",
            "n": 1,
        },
    }

    try:
        createResponse = sendJsonRequest(
            createUrl,
            createPayload,
            apiKey,
            headers={"X-DashScope-Async": "enable"},
        )
        taskId = createResponse.get("output", {}).get("task_id")
        if not taskId:
            print("创建任务成功，但响应中没有 task_id。")
            print(json.dumps(createResponse, ensure_ascii=False, indent=2))
            return 1

        print(f"任务创建成功，task_id: {taskId}")

        taskUrl = f"{BASE_URL}/tasks/{taskId}"
        for attempt in range(1, 25):
            taskResponse = sendGetRequest(taskUrl, apiKey)
            taskStatus = taskResponse.get("output", {}).get("task_status")
            print(f"轮询第 {attempt} 次，task_status: {taskStatus}")

            if taskStatus == "SUCCEEDED":
                results = taskResponse.get("output", {}).get("results") or []
                if not results or not results[0].get("url"):
                    print("任务成功，但响应中没有图片 URL。")
                    print(json.dumps(taskResponse, ensure_ascii=False, indent=2))
                    return 1

                imageUrl = results[0]["url"]
                downloadFile(imageUrl, OUTPUT_IMAGE_PATH)
                print(f"测试完成：图片已保存到 {OUTPUT_IMAGE_PATH}")
                return 0

            if taskStatus in {"FAILED", "CANCELED"}:
                print("图片生成任务失败。")
                print(json.dumps(taskResponse, ensure_ascii=False, indent=2))
                return 1

            time.sleep(5)

        print("测试失败：轮询超时，任务未在预期时间内完成。")
        return 1
    except urllib.error.HTTPError as exc:
        errorBody = exc.read().decode("utf-8", errors="replace")
        print(f"测试失败: HTTP {exc.code}", file=sys.stderr)
        print(errorBody, file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"测试失败: 网络错误 {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"测试失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
