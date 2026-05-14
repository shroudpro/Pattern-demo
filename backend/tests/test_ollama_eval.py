import unittest

from scripts.eval_character_analysis_ollama import (
    build_dashscope_request_payload,
    build_prompt,
    build_repair_prompt,
    extract_dashscope_text,
    evaluate_against_baseline,
    extract_json_object,
)


class ExternalLlmEvalTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = {
            "character": "山",
            "shuowenOriginal": "山，宣也。宣气散生万物，有石而高，象形。",
            "shuowenExplanation": "山字以峰峦起伏的轮廓成形，强调高起、稳固、可依凭的自然形态，常被视为地势、骨架与秩序的象征。",
            "imageryAnalysis": "在传统文化里，山既代表高峻与沉稳，也代表修行、隐逸、守望与时间沉积。它既是自然地理对象，也是人格与精神气度的外化形象。",
            "commonImages": ["峰峦", "山石", "层云", "松林", "古寺"],
            "classicalPoems": ["会当凌绝顶，一览众山小。", "空山新雨后，天气晚来秋。", "千山鸟飞绝，万径人踪灭。"],
            "designKeywords": ["layered", "stone texture", "ridge contour", "majestic", "calm"],
            "summary": "山适合转化为具有层峦、石理、留白和纵深感的纹理背景，适合强调厚重、秩序与静观气质。",
        }

    def test_extract_json_object_supports_wrapped_text(self) -> None:
        raw_text = '前置说明 {"character":"山","shuowenOriginal":"山也","shuowenExplanation":"高起之形，象山。","imageryAnalysis":"山与峰石相关，常表现沉稳和高峻。","commonImages":["峰","石","松"],"classicalPoems":["会当凌绝顶","空山新雨后"],"designKeywords":["layered","stone","mountain"],"summary":"适合转化为纹理背景设计。"} 后置说明'
        parsed = extract_json_object(raw_text)
        self.assertEqual(parsed["character"], "山")
        self.assertEqual(len(parsed["commonImages"]), 3)

    def test_build_prompt_contains_strict_quality_requirements(self) -> None:
        prompt = build_prompt("山")
        self.assertIn("必须直接输出完整诗句", prompt)
        self.assertIn("至少 40 字", prompt)
        self.assertIn("不要输出 Markdown", prompt)
        self.assertIn("至少 15 字", prompt)

    def test_build_dashscope_request_payload_uses_responses_shape(self) -> None:
        payload = build_dashscope_request_payload("qwen3.6-35b-a3b", "test prompt")
        self.assertEqual(payload["model"], "qwen3.6-35b-a3b")
        self.assertEqual(payload["input"], "test prompt")
        self.assertFalse(payload["extra_body"]["enable_thinking"])

    def test_extract_dashscope_text_reads_output_blocks(self) -> None:
        response_json = {
            "output": [
                {
                    "content": [
                        {"text": "{\"character\":\"山\"}"},
                    ]
                }
            ]
        }
        self.assertEqual(extract_dashscope_text(response_json), "{\"character\":\"山\"}")

    def test_build_repair_prompt_references_failed_checks(self) -> None:
        prompt = build_repair_prompt(
            character="山",
            previous_output='{"character":"山"}',
            failed_checks=["shuowenExplanation_min_length", "classicalPoems_count"],
        )
        self.assertIn("shuowenExplanation_min_length", prompt)
        self.assertIn("classicalPoems_count", prompt)
        self.assertIn("不要新增说明文字", prompt)

    def test_evaluate_against_baseline_marks_fail_when_required_list_too_short(self) -> None:
        candidate = {
            "character": "山",
            "shuowenOriginal": "山，高也。",
            "shuowenExplanation": "山是高起的地形。",
            "imageryAnalysis": "山代表高峻。",
            "commonImages": ["峰峦", "山石"],
            "classicalPoems": ["会当凌绝顶"],
            "designKeywords": ["layered", "stone"],
            "summary": "山可做背景。",
        }
        result = evaluate_against_baseline(candidate, self.baseline)
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["commonImages_count"]["passed"])
        self.assertFalse(result["checks"]["classicalPoems_count"]["passed"])

    def test_evaluate_against_baseline_accepts_reduced_shuowen_explanation_threshold(self) -> None:
        candidate = {
            "character": "山",
            "shuowenOriginal": "山，宣也。有石而高，象形。",
            "shuowenExplanation": "山象高起之形，也含稳定可依之义。",
            "imageryAnalysis": "山与峰、石、岩、松、层云和隐逸空间相关，也常被视为守望、修行与高峻精神的象征。",
            "commonImages": ["峰峦", "山石", "松林"],
            "classicalPoems": ["会当凌绝顶，一览众山小。", "空山新雨后，天气晚来秋。"],
            "designKeywords": ["layered", "stone texture", "ridge contour"],
            "summary": "山适合转化为具有层次起伏与石理质感的纹理背景，适合海报和包装视觉设计。",
        }
        result = evaluate_against_baseline(candidate, self.baseline)
        self.assertTrue(result["checks"]["shuowenExplanation_min_length"]["passed"])

    def test_evaluate_against_baseline_marks_borderline_for_quality_gaps(self) -> None:
        candidate = {
            "character": "山",
            "shuowenOriginal": "山，象高起之形。",
            "shuowenExplanation": "山表示高起稳固的自然地形，在古代语义中常被视为秩序和依凭的象征。",
            "imageryAnalysis": "山与峰、石、岩、松和隐逸空间相关，常用于表达沉稳、守望与高峻之意。",
            "commonImages": ["峰峦", "山石", "松林"],
            "classicalPoems": ["会当凌绝顶，一览众山小。", "空山新雨后，天气晚来秋。"],
            "designKeywords": ["layered", "stone texture", "majestic"],
            "summary": "山常被用来表达高峻、沉稳与厚重气质。",
        }
        result = evaluate_against_baseline(candidate, self.baseline)
        self.assertEqual(result["verdict"], "borderline")
        self.assertFalse(result["checks"]["summary_mentions_design_translation"]["passed"])


if __name__ == "__main__":
    unittest.main()
