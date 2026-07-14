from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "tools" / "profile_builder.py"
SPEC = importlib.util.spec_from_file_location("profile_builder", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ProfileBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = {
            "name": "source",
            "comfyuiVersion": "v0.27.0",
            "models": [
                {"name": "one", "url": "https://example.com/one"},
                {"name": "two", "url": "https://example.com/two"},
            ],
            "customNodes": [
                {
                    "title": "Required node",
                    "reference": "https://github.com/example/required",
                },
                {
                    "title": "Manager",
                    "reference": "https://github.com/ltdrdata/ComfyUI-Manager",
                },
                {
                    "title": "Downloader",
                    "reference": "https://github.com/jnxmx/ComfyUI_HuggingFace_Downloader",
                },
            ],
        }

    def test_indices_are_one_based_and_deduplicated(self) -> None:
        self.assertEqual(builder.parse_indices("2, 1, 2", 2, "model"), [1, 0])

    def test_discovery_tools_are_added_once(self) -> None:
        profile = builder.build_profile(
            self.source,
            "test-profile",
            model_indices=[0],
            node_indices=[0, 1],
            include_discovery=True,
        )
        repositories = [builder.repository_url(node) for node in profile["customNodes"]]
        self.assertEqual(len(repositories), len(set(repositories)))
        self.assertIn(
            "https://github.com/jnxmx/ComfyUI_HuggingFace_Downloader",
            repositories,
        )

    def test_invalid_index_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "valid range"):
            builder.parse_indices("3", 2, "model")


if __name__ == "__main__":
    unittest.main()
