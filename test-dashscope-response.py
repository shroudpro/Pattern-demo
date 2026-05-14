import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict


ENV_PATH = Path(__file__).resolve().parent / ".env"
BASE_URL = "https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1"


def loadEnvFile(envPath: Path) -> Dict[str, str]:
    """
    只读取根目录 .env，并兼容 key 前后意外空格的写法，保证快速联调可用。
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
    按用户要求只依赖 .env，同时允许系统环境变量覆盖，方便重复测试。
    """
    envValues = loadEnvFile(ENV_PATH)
    apiKey = os.getenv("DASHSCOPE_API_KEY") or envValues.get("DASHSCOPE_API_KEY")
    if not apiKey:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY，请检查根目录 .env。")
    return apiKey


def extractText(responseJson: Dict) -> str:
    """
    DashScope 兼容接口可能返回多种 output 结构，这里做最小兼容解析。
    """
    output = responseJson.get("output") or []
    texts: list[str] = []

    for item in output:
        for content in item.get("content") or []:
            text = content.get("text")
            if text:
                texts.append(text)

    return "\n".join(texts).strip()


def main() -> int:
    """
    发起一次最小 responses 请求，直接把接口结果打印到终端。
    """
    apiKey = getApiKey()
    endpoint = f"{BASE_URL}/responses"
    payload = {
        "model": "qwen3.6-35b-a3b",
        "input": "请用中文回答：先打一声招呼，再用一句话比较 9.9 和 9.11 哪个更大，并简要解释原因。",
        "extra_body": {
            "enable_thinking": False,
        },
    }

    print("开始测试 DashScope Responses 接口...")
    print(f"endpoint: {endpoint}")
    print(f"model: {payload['model']}")
    print("assistant:")

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {apiKey}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            responseBody = response.read().decode("utf-8")

        responseJson = json.loads(responseBody)
        content = extractText(responseJson)
        if content:
            print(content)
            print("测试完成：已收到有效响应。")
        else:
            print("接口返回成功，但未解析到文本，下面输出原始响应。")
            print(json.dumps(responseJson, ensure_ascii=False, indent=2))
        return 0
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
