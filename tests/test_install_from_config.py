from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).parents[1] / "common" / "install_from_config.py"
SPEC = importlib.util.spec_from_file_location("install_from_config", MODULE_PATH)
assert SPEC and SPEC.loader
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class AuthenticatedDownloadTests(unittest.TestCase):
    def test_required_huggingface_model_needs_token(self) -> None:
        model = {
            "name": "private model",
            "url": "https://huggingface.co/owner/private/resolve/main/model.safetensors",
            "requiresAuth": True,
            "authProvider": "huggingface",
        }
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "HF_TOKEN"):
                installer.authenticated_download(model)

    def test_huggingface_token_becomes_redactable_header(self) -> None:
        model = {
            "url": "https://huggingface.co/owner/private/resolve/main/model.safetensors",
            "requiresAuth": True,
        }
        with mock.patch.dict(os.environ, {"HF_TOKEN": "hf_secret"}, clear=True):
            url, headers, secrets = installer.authenticated_download(model)
        self.assertEqual(url, model["url"])
        self.assertEqual(headers, ["Authorization: Bearer hf_secret"])
        self.assertEqual(secrets, ("hf_secret",))

    def test_civitai_token_is_added_without_destroying_query(self) -> None:
        model = {
            "url": "https://civitai.com/api/download/models/123?type=Model",
            "requiresAuth": True,
            "authProvider": "civitai",
        }
        with mock.patch.dict(
            os.environ, {"CIVITAI_TOKEN": "civitai_secret"}, clear=True
        ):
            url, headers, secrets = installer.authenticated_download(model)
        self.assertIn("type=Model", url)
        self.assertIn("token=civitai_secret", url)
        self.assertEqual(headers, [])
        self.assertEqual(secrets, ("civitai_secret",))

    def test_token_is_not_sent_to_untrusted_host(self) -> None:
        model = {
            "url": "https://example.com/model.safetensors",
            "requiresAuth": True,
            "authProvider": "huggingface",
        }
        with mock.patch.dict(os.environ, {"HF_TOKEN": "hf_secret"}, clear=True):
            with self.assertRaisesRegex(ValueError, "non-Hugging Face"):
                installer.authenticated_download(model)

    def test_hardcoded_civitai_token_is_rejected(self) -> None:
        model = {
            "url": "https://civitai.com/api/download/models/123?token=leaked",
            "authProvider": "civitai",
        }
        with self.assertRaisesRegex(ValueError, "CIVITAI_TOKEN secret"):
            installer.authenticated_download(model)


class SafeCommandTests(unittest.TestCase):
    def test_secret_is_redacted_from_log_and_exception(self) -> None:
        secret = "super-secret-token"
        error = subprocess.CalledProcessError(22, ["curl", f"?token={secret}"])
        output = io.StringIO()
        with mock.patch.object(installer.subprocess, "run", side_effect=error):
            with redirect_stdout(output):
                with self.assertRaises(RuntimeError) as raised:
                    installer.run(
                        ["curl", f"https://example.test/?token={secret}"],
                        secrets=(secret,),
                    )
        self.assertNotIn(secret, output.getvalue())
        self.assertNotIn(secret, str(raised.exception))
        self.assertIn("***", output.getvalue())


class CustomNodeTests(unittest.TestCase):
    def test_optional_editable_failure_does_not_stop_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_nodes = Path(temp_dir)
            target = custom_nodes / "problem-node"
            (target / ".git").mkdir(parents=True)
            (target / "pyproject.toml").write_text("[project]\nname='test'\n")
            node = {"reference": "https://github.com/owner/problem-node"}

            with mock.patch.object(
                installer,
                "run",
                side_effect=subprocess.CalledProcessError(1, ["pip", "install"]),
            ), mock.patch.object(
                installer.subprocess,
                "check_output",
                return_value="a" * 40 + "\n",
            ):
                result = installer.install_node(node, custom_nodes, update_nodes=False)

        self.assertEqual(result["commit"], "a" * 40)


class FileValidationTests(unittest.TestCase):
    def test_partial_large_file_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "model.bin"
            path.write_bytes(b"0" * (96 * 1024 * 1024))
            self.assertFalse(installer.is_complete(path, 100 * 1024 * 1024))

    def test_custom_filename_cannot_escape_destination(self) -> None:
        config = {
            "name": "test",
            "comfyuiVersion": "v0.27.0",
            "models": [
                {
                    "url": "https://example.com/model.bin",
                    "destinationPath": "/workspace/ComfyUI/models/checkpoints",
                    "customFilename": "../escape.bin",
                }
            ],
            "customNodes": [],
        }
        with self.assertRaisesRegex(ValueError, "customFilename"):
            installer.validate_config(config)

    def test_pinned_node_requires_full_commit_sha(self) -> None:
        config = {
            "name": "test",
            "comfyuiVersion": "v0.27.0",
            "models": [],
            "customNodes": [
                {
                    "reference": "https://github.com/owner/node",
                    "commit": "abc1234",
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "40-character SHA"):
            installer.validate_config(config)


if __name__ == "__main__":
    unittest.main()
