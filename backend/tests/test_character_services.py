import json
import unittest
from unittest.mock import patch

from app.core.config import settings
from app.service.character_analysis_service import generate_analysis_payload, get_mock_analysis_payload_by_character, has_mock_analysis_payload
from app.service.character_validation_service import validate_character
from app.service.prompt_composer_service import compose_prompt


class CharacterServicesTestCase(unittest.TestCase):
    def test_validate_character_accepts_whitelist_character(self) -> None:
        result = validate_character("山")
        self.assertTrue(result.validated)
        self.assertEqual(result.character, "山")

    def test_validate_character_rejects_non_whitelist_character(self) -> None:
        result = validate_character("火")
        self.assertTrue(result.validated)
        self.assertEqual(result.character, "火")

    def test_compose_prompt_maps_16x9_to_dashscope_safe_size_and_requests_final_infographic(self) -> None:
        result = compose_prompt(
            character="山",
            analysis={
                "character": "山",
                "summary": "山象征高峻、沉稳、层峦与时间感。",
                "visualMotifs": ["层峦", "云气", "石脉"],
                "colorPalette": ["墨黑", "石青", "云白"],
                "atmosphereTags": ["高远", "静穆"],
                "forbiddenElements": ["现代城市高楼"],
            },
            style_preset="traditional",
            ratio_preset="16:9",
            user_prompt="增加水墨留白和蓝金色水纹",
        )
        self.assertEqual(result.width, 1280)
        self.assertEqual(result.height, 720)
        self.assertEqual(result.width % 8, 0)
        self.assertEqual(result.height % 8, 0)
        self.assertEqual(result.ratioPreset, "16:9")
        self.assertIn("finished Chinese character cultural interpretation infographic", result.positivePrompt)
        self.assertIn("Required visible Chinese title: 山", result.positivePrompt)
        self.assertIn("增加水墨留白和蓝金色水纹", result.positivePrompt)
        self.assertIn("Required right-side content panels", result.positivePrompt)
        self.assertIn("说文解字", result.positivePrompt)
        self.assertIn("常见诗词", result.positivePrompt)
        self.assertNotIn("no text", result.positivePrompt)
        self.assertIn("unreadable body copy", result.negativePrompt)
        self.assertNotIn("malformed Chinese characters", result.negativePrompt)

    def test_analysis_payload_comes_from_local_mock_dataset(self) -> None:
        result = get_mock_analysis_payload_by_character("山")
        self.assertEqual(result.character, "山")
        self.assertGreaterEqual(len(result.classicalPoems), 2)
        self.assertGreaterEqual(len(result.designKeywords), 3)
        self.assertGreaterEqual(len(result.poems), 2)
        self.assertGreaterEqual(len(result.literaryQuotes), 8)
        self.assertTrue(all(item.text and item.source and item.keywords for item in result.literaryQuotes))
        self.assertGreaterEqual(len(result.visualMotifs), 3)
        self.assertIn("精神", result.subtitle)
        self.assertIn("山", result.summary)

    def test_has_mock_analysis_payload_uses_expanded_dataset(self) -> None:
        with settings.mock_character_analysis_path.open("r", encoding="utf-8") as file:
            dataset = json.load(file)

        self.assertGreaterEqual(len(dataset), 100)
        self.assertTrue(has_mock_analysis_payload("山"))

    def test_generate_analysis_payload_uses_llm_when_provider_returns_valid_json(self) -> None:
        class FakeProvider:
            def generate(self, prompt: str) -> dict:
                return {
                    "provider": "dashscope-text",
                    "model": "qwen3.6-35b-a3b",
                    "rawText": """
                    {
                      "character": "龘",
                      "shuowenOriginal": "龘，群龙腾跃之状也，象众势并起之形。",
                      "shuowenExplanation": "此字以重叠龙形构成，强调腾跃、繁盛与极强动势，也可引申为威仪与能量聚合。",
                      "imageryAnalysis": "龘可联想到群龙翻腾、云气盘旋、威仪流动与高密度装饰结构，具有强烈的节奏感、层叠感和视觉张力，适合构建高饱和、高动势的东方图案语汇。",
                      "literaryQuotes": [
                        {"text": "云龙风虎尽交回，太白入月敌可摧。", "source": "李白《司马将军歌》", "keywords": ["龙"]},
                        {"text": "龙衔宝盖承朝日，凤吐流苏带晚霞。", "source": "卢照邻《长安古意》", "keywords": ["龙"]},
                        {"text": "斯须九重真龙出，一洗万古凡马空。", "source": "杜甫《丹青引赠曹将军霸》", "keywords": ["龙"]},
                        {"text": "水不在深，有龙则灵。", "source": "刘禹锡《陋室铭》", "keywords": ["龙"]},
                        {"text": "积水成渊，蛟龙生焉。", "source": "荀子《劝学》", "keywords": ["龙"]},
                        {"text": "还似旧时游上苑，车如流水马如龙。", "source": "李煜《望江南》", "keywords": ["龙"]},
                        {"text": "黑潭水深黑如墨，传有神龙人不识。", "source": "白居易《黑潭龙》", "keywords": ["龙"]},
                        {"text": "山不在高，有仙则名。水不在深，有龙则灵。", "source": "刘禹锡《陋室铭》", "keywords": ["龙"]}
                      ],
                      "commonImages": ["群龙盘旋", "云气回卷", "密集鳞纹"],
                      "classicalPoems": ["黑云翻墨未遮山，白雨跳珠乱入船。", "云龙风虎尽交回，太白入月敌可摧。"],
                      "designKeywords": ["ornamental density", "rhythmic contour", "dynamic pattern"],
                      "summary": "龘适合转译为高密度、强节奏、富有动势的纹理背景，可用于强调视觉冲击力的海报与包装设计。"
                    }
                    """,
                }

        with patch("app.service.character_analysis_service._get_text_provider", return_value=FakeProvider()):
            analysis, meta = generate_analysis_payload("龘")

        self.assertEqual(meta["source"], "llm")
        self.assertFalse(meta["fallbackUsed"])
        self.assertEqual(analysis.character, "龘")
        self.assertGreaterEqual(len(analysis.classicalPoems), 2)
        self.assertGreaterEqual(len(analysis.poems), 2)
        self.assertGreaterEqual(len(analysis.literaryQuotes), 8)
        self.assertGreaterEqual(len(analysis.visualMotifs), 3)

    def test_build_character_analysis_prompt_requests_literary_quotes(self) -> None:
        from app.service.character_analysis_service import build_character_analysis_prompt

        prompt = build_character_analysis_prompt("山")
        self.assertIn("literaryQuotes", prompt)
        self.assertIn("至少 8 条", prompt)
        self.assertIn("text、source、keywords", prompt)

    def test_generate_analysis_payload_rejects_llm_with_too_few_literary_quotes(self) -> None:
        class IncompleteProvider:
            def generate(self, prompt: str) -> dict:
                return {
                    "provider": "dashscope-text",
                    "model": "qwen3.6-35b-a3b",
                    "rawText": """
                    {
                      "character": "龘",
                      "shuowenOriginal": "龘，群龙腾跃之状也，象众势并起之形。",
                      "shuowenExplanation": "此字以重叠龙形构成，强调腾跃、繁盛与极强动势，也可引申为威仪与能量聚合。",
                      "imageryAnalysis": "龘可联想到群龙翻腾、云气盘旋、威仪流动与高密度装饰结构，具有强烈的节奏感、层叠感和视觉张力，适合构建高饱和、高动势的东方图案语汇。",
                      "literaryQuotes": [
                        {"text": "云龙风虎尽交回，太白入月敌可摧。", "source": "李白《司马将军歌》", "keywords": ["龙"]}
                      ],
                      "commonImages": ["群龙盘旋", "云气回卷", "密集鳞纹"],
                      "classicalPoems": ["云龙风虎尽交回，太白入月敌可摧。", "龙衔宝盖承朝日，凤吐流苏带晚霞。"],
                      "designKeywords": ["ornamental density", "rhythmic contour", "dynamic pattern"],
                      "summary": "龘适合转译为高密度、强节奏、富有动势的东方图案，可表现群龙聚合的视觉冲击。"
                    }
                    """,
                }

        with patch("app.service.character_analysis_service._get_text_provider", return_value=IncompleteProvider()):
            with self.assertRaises(ValueError) as context:
                generate_analysis_payload("龘")

        self.assertIn("literaryQuotes", str(context.exception))

    def test_generate_analysis_payload_uses_mock_directly_when_character_in_dataset(self) -> None:
        with patch("app.service.character_analysis_service._get_text_provider") as mocked_provider:
            analysis, meta = generate_analysis_payload("山")

        mocked_provider.assert_not_called()
        self.assertEqual(meta["source"], "mock")
        self.assertFalse(meta["fallbackUsed"])
        self.assertEqual(meta["provider"], "mock-local-dataset")
        self.assertEqual(analysis.character, "山")

    def test_generate_analysis_payload_raises_when_character_missing_and_provider_fails(self) -> None:
        class BrokenProvider:
            def generate(self, prompt: str) -> dict:
                raise RuntimeError("remote failed")

        with patch("app.service.character_analysis_service._get_text_provider", return_value=BrokenProvider()):
            with self.assertRaises(ValueError) as context:
                generate_analysis_payload("龘")

        self.assertIn("外接模型生成失败", str(context.exception))


if __name__ == "__main__":
    unittest.main()
