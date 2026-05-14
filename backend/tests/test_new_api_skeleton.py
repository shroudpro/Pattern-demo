import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.database import engine
from app.main import app
from app.providers.mock import MockImageGenerationProvider


class NewApiSkeletonTestCase(unittest.TestCase):
    def setUp(self) -> None:
        analysis_patcher = patch("app.service.character_analysis_service._get_text_provider", return_value=None)
        image_patcher = patch("app.service.image_generation_service._get_image_provider", return_value=MockImageGenerationProvider())
        self.addCleanup(analysis_patcher.stop)
        self.addCleanup(image_patcher.stop)
        analysis_patcher.start()
        image_patcher.start()
        self.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        engine.dispose()

    def test_create_analysis_session_returns_expected_shape(self) -> None:
        response = self.client.post("/api/v1/analysis-sessions", json={"character": "山"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["character"], "山")
        self.assertIn("shuowenOriginal", payload["analysis"])
        self.assertIn("modernMeaning", payload["analysis"])
        self.assertGreaterEqual(len(payload["analysis"]["visualMotifs"]), 3)
        self.assertGreaterEqual(len(payload["analysis"]["poems"]), 2)
        self.assertGreaterEqual(len(payload["analysis"]["literaryQuotes"]), 8)
        self.assertIn("source", payload["analysis"]["literaryQuotes"][0])
        self.assertIn("keywords", payload["analysis"]["literaryQuotes"][0])
        self.assertIn("author", payload["analysis"]["poems"][0])
        detail_response = self.client.get(f"/api/v1/analysis-sessions/{payload['id']}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["analysis"]["summary"], payload["analysis"]["summary"])

    def test_get_project_missing_returns_404(self) -> None:
        response = self.client.get("/api/v1/projects/999999")
        self.assertEqual(response.status_code, 404)

    def test_image_generation_job_returns_mock_image_url(self) -> None:
        analysis_response = self.client.post("/api/v1/analysis-sessions", json={"character": "山"})
        analysis_payload = analysis_response.json()

        response = self.client.post(
            "/api/v1/image-generation-jobs",
            json={
                "analysisSessionId": analysis_payload["id"],
                "character": analysis_payload["character"],
                "analysis": analysis_payload["analysis"],
                "stylePreset": "traditional",
                "ratioPreset": "16:9",
            },
        )
        self.assertEqual(response.status_code, 200)
        created_job = response.json()
        detail_response = self.client.get(f"/api/v1/image-generation-jobs/{created_job['id']}")
        self.assertEqual(detail_response.status_code, 200)
        detail_payload = detail_response.json()
        self.assertEqual(detail_payload["status"], "succeeded")
        self.assertTrue(str(detail_payload["outputUrl"]).endswith(".png"))
        self.assertFalse(detail_payload["fallbackUsed"])
        self.assertEqual(detail_payload["ratioPreset"], "16:9")
        self.assertIn("positivePrompt", detail_payload)
        self.assertIn("finished Chinese character cultural interpretation infographic", detail_payload["positivePrompt"])
        self.assertIn("Required right-side content panels", detail_payload["positivePrompt"])
        self.assertNotIn("no text", detail_payload["positivePrompt"])
        self.assertIn("unreadable body copy", detail_payload["negativePrompt"])
        self.assertNotIn("malformed Chinese characters", detail_payload["negativePrompt"])

    def test_project_patch_updates_elements(self) -> None:
        create_response = self.client.post(
            "/api/v1/projects",
            json={
                "character": "山",
                "analysisSessionId": 1,
                "imageJobId": 1,
                "backgroundImageUrl": "/mock/textures/poster-traditional.png",
                "canvasWidth": 864,
                "canvasHeight": 1152,
                "layoutSpec": {
                    "version": 1,
                    "projectType": "infographic",
                    "backgroundOpacity": 1,
                    "layers": [],
                },
                "elements": [],
            },
        )
        self.assertEqual(create_response.status_code, 200)
        project_payload = create_response.json()

        patch_response = self.client.patch(
            f"/api/v1/projects/{project_payload['id']}",
            json={
                "elements": [
                    {
                        "id": "text-1",
                        "type": "text",
                        "left": 120,
                        "top": 160,
                        "text": "山海",
                    }
                ],
                "layoutSpec": {
                    "version": 1,
                    "projectType": "infographic",
                    "backgroundOpacity": 0.75,
                    "layers": [],
                },
            },
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["elements"][0]["text"], "山海")
        self.assertEqual(patch_response.json()["layoutSpec"]["backgroundOpacity"], 0.75)

        detail_response = self.client.get(f"/api/v1/projects/{project_payload['id']}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["elements"][0]["text"], "山海")
        self.assertEqual(detail_response.json()["layoutSpec"]["backgroundOpacity"], 0.75)

    def test_cors_preflight_allows_frontend_origin(self) -> None:
        response = self.client.options(
            "/api/v1/analysis-sessions",
            headers={
                "Origin": "http://127.0.0.1:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://127.0.0.1:3000")

    def test_cors_preflight_allows_alternate_next_dev_port(self) -> None:
        response = self.client.options(
            "/api/v1/analysis-sessions",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:3001")

    def test_cors_preflight_allows_dynamic_localhost_dev_port(self) -> None:
        response = self.client.options(
            "/api/v1/analysis-sessions",
            headers={
                "Origin": "http://localhost:3999",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:3999")


if __name__ == "__main__":
    unittest.main()
