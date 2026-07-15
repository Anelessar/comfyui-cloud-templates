import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_IMAGE = "vastai/comfy:v0.27.0-cuda-13.2-py312"
OFFICIAL_COMFY_PORTAL = "localhost:8188:18188:/:ComfyUI"


class VastPortalConfigTests(unittest.TestCase):
    def test_documented_templates_use_the_official_comfy_image_and_proxy_port(self):
        paths = (
            ROOT / "README.md",
            ROOT / "providers" / "vastai" / "image-template.md",
            ROOT / "providers" / "vastai" / "video-template.md",
        )

        for path in paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                self.assertIn(OFFICIAL_IMAGE, content)
                self.assertIn(OFFICIAL_COMFY_PORTAL, content)
                self.assertNotIn("127.0.0.1:8188:8188:/:ComfyUI", content)

    def test_vast_provisioning_delegates_service_startup_to_official_image(self):
        provision = (ROOT / "providers" / "vastai" / "provision.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("EXPECTED_COMFY_VERSION", provision)
        self.assertIn("--phase nodes", provision)
        self.assertIn("--phase models", provision)
        self.assertIn("models.pid", provision)
        self.assertNotIn("start-comfyui.sh", provision)
        self.assertNotIn("python -m http.server", provision)
        self.assertNotIn("--listen", provision)

    def test_model_downloads_start_after_nodes_and_run_in_background(self):
        provision = (ROOT / "providers" / "vastai" / "provision.sh").read_text(
            encoding="utf-8"
        )

        nodes_phase = provision.index("--phase nodes")
        nohup_models = provision.index("nohup python")
        models_phase = provision.index("--phase models", nohup_models)
        self.assertLess(nodes_phase, nohup_models)
        self.assertLess(nohup_models, models_phase)

    def test_check_script_supports_official_supervisor_and_runpod(self):
        check = (ROOT / "common" / "check-install.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("supervisorctl status comfyui", check)
        self.assertIn('COMFY_PORT:-18188', check)
        self.assertIn('COMFY_PORT:-8188', check)
        self.assertIn("/system_stats", check)


if __name__ == "__main__":
    unittest.main()
