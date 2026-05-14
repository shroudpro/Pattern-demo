import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings

REQUIRED_FIELDS = (
    "character",
    "shuowenOriginal",
    "shuowenExplanation",
    "imageryAnalysis",
    "commonImages",
    "classicalPoems",
    "designKeywords",
    "summary",
)
STRING_FIELDS = ("shuowenOriginal", "shuowenExplanation", "imageryAnalysis", "summary")
LIST_FIELDS = ("commonImages", "classicalPoems", "designKeywords")
MIN_LENGTHS = {
    "shuowenOriginal": 8,
    "shuowenExplanation": 15,
    "imageryAnalysis": 40,
    "summary": 30,
}
MIN_COUNTS = {
    "commonImages": 3,
    "classicalPoems": 2,
    "designKeywords": 3,
}
PLACEHOLDER_TOKENS = ("示例", "占位", "待补充", "TODO")
MOUNTAIN_TOKENS = ("山", "峰", "峦", "石", "高", "岩", "松", "隐")
DESIGN_TOKENS = ("设计", "纹理", "背景", "视觉", "转化")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="评测外接 LLM 是否满足纹生万象第一阶段单字分析要求。")
    parser.add_argument("--character", default="山", help="待评测单字，默认山。")
    parser.add_argument("--model", default=settings.dashscope_model_name, help="外接模型名。")
    parser.add_argument("--base-url", default=settings.dashscope_base_url, help="DashScope 兼容接口地址。")
    return parser.parse_args()


def load_baseline(character: str) -> dict[str, Any]:
    with settings.mock_character_analysis_path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if character not in dataset:
        raise ValueError(f"mock 数据中不存在字符「{character}」。文件={settings.mock_character_analysis_path}")

    return dataset[character]


def build_prompt(character: str) -> str:
    schema = {
        "character": character,
        "shuowenOriginal": "string",
        "shuowenExplanation": "string",
        "imageryAnalysis": "string",
        "commonImages": ["string", "string", "string"],
        "classicalPoems": ["string", "string"],
        "designKeywords": ["string", "string", "string"],
        "summary": "string",
    }
    return (
        "你是“纹生万象”项目第一阶段汉字文化分析模块。\n"
        f"请针对单字“{character}”输出一个严格合法的 JSON 对象。\n"
        "不要输出 Markdown，不要输出代码块，不要输出解释，不要输出前后缀文字。\n"
        "输出必须能被 Python json.loads 直接解析，必须使用标准 JSON 双引号，不能使用中文引号，不能使用顿号替代逗号。\n"
        "输出语言为简体中文，designKeywords 可中英混合，但整体内容必须适合产品展示，不能写成词典释义或泛泛而谈的百科说明。\n"
        "要求：\n"
        "0. 你必须一次性产出高质量最终答案，不要保守简写，不要为了简洁省略内容。\n"
        "1. commonImages、classicalPoems、designKeywords 必须是 JSON 数组。\n"
        "2. commonImages 至少 3 项，必须是具体意象，不要写“图片”“示意图”“风光图片”。\n"
        "3. classicalPoems 至少 2 条，必须直接输出完整诗句，不得写“《诗经》中的高山”这种转述或标题。\n"
        "4. designKeywords 至少 3 项，必须是适合设计转译的关键词，避免空泛口号。\n"
        "5. shuowenOriginal 必须模拟《说文解字》原文风格，写成完整文言句，不能只写单字，至少 8 字。\n"
        "6. shuowenOriginal 的句式应类似“山，……也。……，象形。”这种完整原文格式。\n"
        "7. shuowenExplanation 至少 15 字，建议 40 字以上，必须解释字形与文化义项。\n"
        "8. imageryAnalysis 至少 40 字，必须写出山相关意象，例如峰峦、山石、层云、松林、隐逸、守望等。\n"
        "9. summary 至少 30 字，必须明确体现面向设计转译、纹理背景或视觉应用的结论。\n"
        "10. 不得出现示例、占位、待补充、TODO 等占位词。\n"
        "11. 不得输出“汉字，形声字”这类与项目目标无关的简略词典式开头。\n"
        "12. classicalPoems 应优先选取广为人知、语义准确、和“山”直接相关的诗句，每条尽量带有明确山景或登临语境。\n"
        "13. designKeywords 应偏向可用于图案纹理、背景视觉、海报底纹、包装肌理的描述，不要只写抽象审美词。\n"
        "14. summary 需要明确指出该字适合转译成怎样的背景纹理结构、视觉层次或材质方向。\n"
        "请严格使用以下字段结构：\n"
        f"{json.dumps(schema, ensure_ascii=False)}"
    )


def build_dashscope_request_payload(model: str, prompt: str) -> dict[str, Any]:
    return {
        "model": model,
        "input": prompt,
        "extra_body": {
            "enable_thinking": False,
        },
    }


def extract_dashscope_text(response_json: dict[str, Any]) -> str:
    output = response_json.get("output") or []
    texts: list[str] = []

    for item in output:
        for content in item.get("content") or []:
            text = content.get("text")
            if text:
                texts.append(text)

    return "\n".join(texts).strip()


def build_repair_prompt(character: str, previous_output: str, failed_checks: list[str]) -> str:
    return (
        f"你上一次为单字“{character}”生成的 JSON 未通过校验。\n"
        "请在保持原有 8 个字段不变的前提下，只修复失败项并重新输出一个严格合法的 JSON 对象。\n"
        "不要新增说明文字，不要输出 Markdown，不要输出代码块，不要输出前后缀。\n"
        "必须使用标准 JSON 双引号，数组必须是合法 JSON 数组。\n"
        f"失败项：{', '.join(failed_checks)}。\n"
        "修复重点：\n"
        "- shuowenOriginal 必须是完整《说文》风格文言句，不得只写单字。\n"
        "- shuowenExplanation 必须不少于 15 字，且应尽量写到 40 字以上以保证解释充分。\n"
        "- classicalPoems 必须是至少 2 条完整诗句，每条单独作为数组项。\n"
        "- 不得出现“《诗经》中的高山”之类转述标题。\n"
        "- summary 必须明确提到设计、纹理、背景、视觉或转化中的至少一个词。\n"
        "上一次输出如下，请直接在其基础上修复：\n"
        f"{previous_output}"
    )


def call_dashscope(base_url: str, model: str, prompt: str) -> str:
    if not settings.dashscope_api_key:
        raise RuntimeError("DASHSCOPE_API_KEY 未配置，无法调用外接模型。")

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/responses",
        data=json.dumps(build_dashscope_request_payload(model, prompt), ensure_ascii=False).encode("utf-8"),
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
    raw_response = extract_dashscope_text(response_json)
    if not raw_response:
        raise RuntimeError(f"DashScope 返回成功但未解析到文本，原始响应：{json.dumps(response_json, ensure_ascii=False)}")

    return raw_response


def extract_json_object(raw_text: str) -> dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start_index = raw_text.find("{")
        end_index = raw_text.rfind("}")
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            raise
        return json.loads(raw_text[start_index : end_index + 1])


def _text_length(value: Any) -> int:
    return len(value.strip()) if isinstance(value, str) else 0


def _list_count(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _all_strings(values: Any) -> bool:
    return isinstance(values, list) and all(isinstance(item, str) for item in values)


def evaluate_against_baseline(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [field for field in REQUIRED_FIELDS if field not in candidate]
    field_types_valid = not missing_fields and all(isinstance(candidate[field], str) for field in STRING_FIELDS) and all(
        isinstance(candidate[field], list) for field in LIST_FIELDS
    )
    checks: dict[str, dict[str, Any]] = {
        "json_parseable": {"passed": True, "detail": "模型输出可解析为 JSON。"},
        "required_fields_complete": {"passed": not missing_fields, "detail": f"缺失字段：{missing_fields or '无'}"},
        "field_types_valid": {"passed": field_types_valid, "detail": "文本字段为字符串，列表字段为数组。"},
        "character_match": {
            "passed": candidate.get("character") == baseline["character"],
            "detail": f"模型字符={candidate.get('character')!r}",
        },
    }

    metrics: dict[str, dict[str, Any]] = {}

    for field_name, threshold in MIN_LENGTHS.items():
        candidate_length = _text_length(candidate.get(field_name))
        baseline_length = _text_length(baseline.get(field_name))
        passed = candidate_length >= threshold
        checks[f"{field_name}_min_length"] = {
            "passed": passed,
            "detail": f"模型长度={candidate_length}，阈值={threshold}",
        }
        metrics[field_name] = {
            "baselineLength": baseline_length,
            "modelLength": candidate_length,
            "baselineLengthRatio": round(candidate_length / baseline_length, 3) if baseline_length else None,
        }

    for field_name, threshold in MIN_COUNTS.items():
        candidate_count = _list_count(candidate.get(field_name))
        baseline_count = _list_count(baseline.get(field_name))
        passed = candidate_count >= threshold
        checks[f"{field_name}_count"] = {
            "passed": passed,
            "detail": f"模型数量={candidate_count}，阈值={threshold}",
        }
        metrics[field_name] = {
            **metrics.get(field_name, {}),
            "baselineCount": baseline_count,
            "modelCount": candidate_count,
            "baselineCountRatio": round(candidate_count / baseline_count, 3) if baseline_count else None,
        }

    string_values = [str(candidate.get(field_name, "")) for field_name in STRING_FIELDS]
    list_values = candidate.get("commonImages", []) + candidate.get("classicalPoems", []) + candidate.get("designKeywords", [])
    checks["no_placeholder_language"] = {
        "passed": not any(token in "".join(string_values + [str(item) for item in list_values]) for token in PLACEHOLDER_TOKENS),
        "detail": "检查是否包含示例、占位、待补充、TODO。",
    }
    checks["imagery_mentions_mountain_semantics"] = {
        "passed": any(token in str(candidate.get("imageryAnalysis", "")) for token in MOUNTAIN_TOKENS),
        "detail": "检查 imageryAnalysis 是否命中山相关语义词。",
    }
    checks["summary_mentions_design_translation"] = {
        "passed": any(token in str(candidate.get("summary", "")) for token in DESIGN_TOKENS),
        "detail": "检查 summary 是否提到设计、纹理、背景、视觉或转化。",
    }
    checks["poems_look_like_poems"] = {
        "passed": _all_strings(candidate.get("classicalPoems")) and all(_text_length(item) >= 5 for item in candidate.get("classicalPoems", [])),
        "detail": "检查古诗词数组项是否为非空中文句子。",
    }

    hard_fail_keys = (
        "required_fields_complete",
        "field_types_valid",
        "character_match",
        "commonImages_count",
        "classicalPoems_count",
        "designKeywords_count",
    )
    if not all(checks[key]["passed"] for key in hard_fail_keys):
        verdict = "fail"
    else:
        failed_quality_checks = [name for name, item in checks.items() if not item["passed"] and name not in hard_fail_keys and name != "json_parseable"]
        verdict = "pass" if not failed_quality_checks else ("borderline" if len(failed_quality_checks) <= 3 else "fail")

    summary = build_summary(verdict, checks)
    return {
        "checks": checks,
        "metrics": metrics,
        "verdict": verdict,
        "summary": summary,
    }


def build_summary(verdict: str, checks: dict[str, dict[str, Any]]) -> str:
    failed_checks = [name for name, item in checks.items() if not item["passed"]]
    if verdict == "pass":
        return "模型输出通过当前第一阶段最低结构与质量要求。"
    if verdict == "borderline":
        return f"模型输出结构合格，但仍有质量短板：{', '.join(failed_checks)}。"
    return f"模型输出未满足第一阶段要求，关键失败项：{', '.join(failed_checks)}。"


def build_parse_failure_result(raw_response: str, baseline: dict[str, Any], prompt: str, model: str, base_url: str) -> dict[str, Any]:
    checks = {
        "json_parseable": {"passed": False, "detail": "模型输出无法解析为 JSON。"},
    }
    return {
        "character": baseline["character"],
        "provider": "dashscope",
        "model": model,
        "baseUrl": base_url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "rawResponse": raw_response,
        "parsedResponse": None,
        "baseline": baseline,
        "checks": checks,
        "metrics": {},
        "verdict": "fail",
        "summary": "模型输出无法解析为合法 JSON，因此不符合第一阶段结构要求。",
    }


def build_result(
    character: str,
    model: str,
    base_url: str,
    prompt: str,
    raw_response: str,
    baseline: dict[str, Any],
) -> dict[str, Any]:
    try:
        parsed_response = extract_json_object(raw_response)
        evaluation = evaluate_against_baseline(parsed_response, baseline)
        return {
            "character": character,
            "provider": "dashscope",
            "model": model,
            "baseUrl": base_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "rawResponse": raw_response,
            "parsedResponse": parsed_response,
            "baseline": baseline,
            "checks": evaluation["checks"],
            "metrics": evaluation["metrics"],
            "verdict": evaluation["verdict"],
            "summary": evaluation["summary"],
        }
    except Exception:
        return build_parse_failure_result(
            raw_response=raw_response,
            baseline=baseline,
            prompt=prompt,
            model=model,
            base_url=base_url,
        )


def verdict_rank(verdict: str) -> int:
    if verdict == "pass":
        return 3
    if verdict == "borderline":
        return 2
    return 1


def print_report(result: dict[str, Any], baseline_path: Path) -> None:
    print("=== 运行配置 ===")
    print(f"provider: {result['provider']}")
    print(f"model: {result['model']}")
    print(f"base_url: {result['baseUrl']}")
    print(f"character: {result['character']}")
    print(f"mock_file: {baseline_path}")
    print()

    print("=== 原始模型输出 ===")
    raw_response = result["rawResponse"]
    if len(raw_response) > 4000:
        print(f"{raw_response[:4000]}\n...<truncated>...")
    else:
        print(raw_response)
    print()

    print("=== 解析结果摘要 ===")
    parsed_response = result["parsedResponse"]
    print(f"parseable_json: {result['checks'].get('json_parseable', {}).get('passed', False)}")
    if parsed_response:
        missing_fields = [field for field in REQUIRED_FIELDS if field not in parsed_response]
        print(f"missing_fields: {missing_fields or '无'}")
        for field_name in STRING_FIELDS:
            print(f"{field_name}_length: {_text_length(parsed_response.get(field_name))}")
        for field_name in LIST_FIELDS:
            print(f"{field_name}_count: {_list_count(parsed_response.get(field_name))}")
    print()

    print("=== 字段级对比 ===")
    for field_name in REQUIRED_FIELDS:
        metric = result["metrics"].get(field_name, {})
        if field_name in STRING_FIELDS:
            print(
                f"{field_name}: baseline_length={metric.get('baselineLength')} "
                f"model_length={metric.get('modelLength')} "
                f"ratio={metric.get('baselineLengthRatio')}"
            )
        else:
            print(
                f"{field_name}: baseline_count={metric.get('baselineCount')} "
                f"model_count={metric.get('modelCount')} "
                f"ratio={metric.get('baselineCountRatio')}"
            )
    for check_name, check_value in result["checks"].items():
        print(f"{check_name}: {'PASS' if check_value['passed'] else 'FAIL'} - {check_value['detail']}")
    print()

    print("=== 最终结论 ===")
    print(result["verdict"].upper())
    print(result["summary"])


def write_result(result: dict[str, Any]) -> Path:
    output_dir = settings.project_root / "outputs" / "llm-evals"
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = "shan" if result["character"] == "山" else result["character"]
    model_slug = str(result["model"]).replace(":", "-").replace("/", "-")
    file_name = f"{slug}-{model_slug}-eval.json"
    output_path = output_dir / file_name
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> int:
    args = parse_args()
    try:
        baseline = load_baseline(args.character)
    except Exception as exc:
        print(f"读取 mock 数据失败：{exc}", file=sys.stderr)
        return 1

    prompt = build_prompt(args.character)

    try:
        raw_response = call_dashscope(args.base_url, args.model, prompt)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    result = build_result(
        character=args.character,
        model=args.model,
        base_url=args.base_url,
        prompt=prompt,
        raw_response=raw_response,
        baseline=baseline,
    )
    result["provider"] = "dashscope"

    failed_checks = [name for name, item in result["checks"].items() if not item["passed"]]
    if result["verdict"] != "pass" and failed_checks:
        repair_prompt = build_repair_prompt(args.character, raw_response, failed_checks)
        try:
            repaired_raw_response = call_dashscope(args.base_url, args.model, repair_prompt)
            repaired_result = build_result(
                character=args.character,
                model=args.model,
                base_url=args.base_url,
                prompt=repair_prompt,
                raw_response=repaired_raw_response,
                baseline=baseline,
            )
            repaired_result["provider"] = "dashscope"
            repaired_result["previousAttempt"] = result
            if verdict_rank(repaired_result["verdict"]) >= verdict_rank(result["verdict"]):
                result = repaired_result
        except Exception:
            pass

    output_path = write_result(result)
    print_report(result, settings.mock_character_analysis_path)
    print()
    print(f"结果文件已写入：{output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
