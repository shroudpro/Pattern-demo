import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from app.providers.dashscope_image import (
    format_dashscope_size,
    get_dashscope_result_url,
    get_dashscope_task_id,
    get_dashscope_task_status,
    normalize_to_multiple_of_8,
)
from app.service.image_generation_service import _process_dashscope_generation_job
from app.service.image_generation_service import _resolve_fallback_generated_image
from app.service.image_generation_service import process_image_generation_job


class ImageGenerationServiceTestCase(unittest.TestCase):
    def test_resolve_fallback_generated_image_returns_final_template(self) -> None:
        traditional = _resolve_fallback_generated_image("traditional")
        modern = _resolve_fallback_generated_image("modern")
        shan_demo = _resolve_fallback_generated_image({"character": "山", "stylePreset": "traditional", "ratioPreset": "16:9"})

        self.assertIsNotNone(traditional)
        self.assertEqual(traditional["outputUrl"], "/img/D1.png")
        self.assertIsNotNone(modern)
        self.assertEqual(modern["outputUrl"], "/img/D2.png")
        self.assertIsNotNone(shan_demo)
        self.assertEqual(shan_demo["outputUrl"], "/img/F1.png")

    def test_process_image_generation_job_uses_template_when_provider_fails(self) -> None:
        provider = MagicMock()
        provider.generate_texture.side_effect = RuntimeError("remote image api unavailable")
        record = MagicMock()
        record.payload = (
            '{"width":1280,"height":720,"positivePrompt":"finished infographic",'
            '"character":"山","stylePreset":"traditional","ratioPreset":"16:9","scenePreset":"poster"}'
        )
        record.created_at = datetime.now(timezone.utc)
        db = MagicMock()
        session_context = MagicMock()
        session_context.__enter__.return_value = db
        session_context.__exit__.return_value = None

        with unittest.mock.patch("app.service.image_generation_service.SessionLocal", return_value=session_context):
            with unittest.mock.patch("app.service.image_generation_service.get_image_job", return_value=record):
                with unittest.mock.patch("app.service.image_generation_service._get_image_provider", return_value=provider):
                    with unittest.mock.patch("app.service.image_generation_service.update_image_job") as update_mock:
                        process_image_generation_job(1)

        final_update = update_mock.call_args_list[-1].kwargs
        self.assertEqual(final_update["status"], "succeeded")
        self.assertEqual(final_update["payload"]["outputUrl"], "/img/F1.png")
        self.assertTrue(final_update["payload"]["fallbackUsed"])
        self.assertIn("本地解析图模板降级", final_update["payload"]["errorMessage"])

    def test_format_dashscope_size_replaces_x_with_asterisk(self) -> None:
        self.assertEqual(format_dashscope_size("864x1152"), "864*1152")

    def test_format_dashscope_size_normalizes_to_multiple_of_8(self) -> None:
        self.assertEqual(format_dashscope_size("1025x777"), "1024*776")
        self.assertEqual(normalize_to_multiple_of_8(720), 720)

    def test_get_dashscope_task_id_returns_task_identifier(self) -> None:
        payload = {"output": {"task_id": "task-123"}}
        self.assertEqual(get_dashscope_task_id(payload), "task-123")

    def test_get_dashscope_result_url_returns_first_result_url(self) -> None:
        payload = {"output": {"results": [{"url": "https://example.com/image.png"}]}}
        self.assertEqual(get_dashscope_result_url(payload), "https://example.com/image.png")

    def test_process_dashscope_generation_job_marks_succeeded_when_remote_job_finishes(self) -> None:
        provider = MagicMock()
        provider.create_task.return_value = {"output": {"task_id": "task-123", "task_status": "PENDING"}}
        provider.get_task.side_effect = [
            {"output": {"task_status": "RUNNING"}},
            {"output": {"task_status": "SUCCEEDED", "results": [{"url": "https://example.com/image.png"}]}},
        ]
        db = MagicMock()
        base_payload = {"positivePrompt": "mountain texture", "character": "山"}

        with unittest.mock.patch("app.service.image_generation_service.persist_generated_image", return_value=("/generated/x.png", "E:/x.png")) as persist_mock:
            with unittest.mock.patch("app.service.image_generation_service.update_image_job") as update_mock:
                with unittest.mock.patch("app.service.image_generation_service.time.sleep"):
                    _process_dashscope_generation_job(
                        db=db,
                        job_id=1,
                        provider=provider,
                        base_payload=base_payload,
                        size="864x1152",
                    )

        persist_mock.assert_called_once()
        self.assertEqual(update_mock.call_args_list[-1].kwargs["status"], "succeeded")
        self.assertEqual(update_mock.call_args_list[-1].kwargs["payload"]["remoteTaskStatus"], "SUCCEEDED")

    def test_process_dashscope_generation_job_raises_on_timeout(self) -> None:
        provider = MagicMock()
        provider.create_task.return_value = {"output": {"task_id": "task-123", "task_status": "PENDING"}}
        provider.get_task.return_value = {"output": {"task_status": "RUNNING"}}
        db = MagicMock()
        base_payload = {"positivePrompt": "mountain texture", "character": "山"}

        with unittest.mock.patch("app.service.image_generation_service.update_image_job"):
            with unittest.mock.patch("app.service.image_generation_service.time.sleep"):
                with self.assertRaises(RuntimeError) as context:
                    _process_dashscope_generation_job(
                        db=db,
                        job_id=1,
                        provider=provider,
                        base_payload=base_payload,
                        size="864x1152",
                    )

        self.assertIn("轮询超时", str(context.exception))

    def test_process_dashscope_generation_job_includes_remote_error_detail(self) -> None:
        provider = MagicMock()
        provider.create_task.return_value = {"output": {"task_id": "task-123", "task_status": "PENDING"}}
        provider.get_task.return_value = {
            "output": {
                "task_status": "FAILED",
                "code": "InvalidParameter",
                "message": "The size does not match the allowed size ['864*1152'].",
            }
        }
        db = MagicMock()
        base_payload = {"positivePrompt": "mountain texture", "character": "山"}

        with unittest.mock.patch("app.service.image_generation_service.update_image_job"):
            with self.assertRaises(RuntimeError) as context:
                _process_dashscope_generation_job(
                    db=db,
                    job_id=1,
                    provider=provider,
                    base_payload=base_payload,
                    size="864x1152",
                )

        self.assertIn("task_status=FAILED", str(context.exception))
        self.assertIn("code=InvalidParameter", str(context.exception))
        self.assertIn("The size does not match", str(context.exception))
