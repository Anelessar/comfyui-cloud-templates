import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECT_COMFY_PORTAL = "localhost:8188:8188:/:ComfyUI"
CONFLICTING_COMFY_PORTAL = ":".join(
    ("localhost", "8188", "18188", "/", "ComfyUI")
)


class VastPortalConfigTests(unittest.TestCase):
    def test_documented_templates_use_the_direct_comfyui_port(self):
        paths = (
            ROOT / "README.md",
            ROOT / "providers" / "vastai" / "image-template.md",
            ROOT / "providers" / "vastai" / "video-template.md",
        )

        for path in paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                self.assertIn(DIRECT_COMFY_PORTAL, content)
                self.assertNotIn(CONFLICTING_COMFY_PORTAL, content)

    def test_vast_provisioning_enables_ipv6_for_the_localhost_tunnel(self):
        provision = (ROOT / "providers" / "vastai" / "provision.sh").read_text(
            encoding="utf-8"
        )
        start = (ROOT / "common" / "start-comfyui.sh").read_text(
            encoding="utf-8"
        )
        check = (ROOT / "common" / "check-install.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("comfy-listen-host", provision)
        self.assertIn("'::'", provision)
        self.assertIn('read -r LISTEN_HOST < "${STATE_DIR}/comfy-listen-host"', start)
        self.assertIn('--listen "${LISTEN_HOST}"', start)
        self.assertIn('HEALTH_HOST="[::1]"', start)
        self.assertIn("comfy-listen-host", check)
        self.assertIn('HEALTH_HOST="[::1]"', check)


if __name__ == "__main__":
    unittest.main()
