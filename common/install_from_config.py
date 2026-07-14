#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit, urlunsplit


def run(
    cmd: list[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    secrets: tuple[str, ...] = (),
) -> None:
    """Run a command without exposing configured secrets in the log."""
    safe_cmd = []
    for item in cmd:
        safe_item = str(item)
        for secret in secrets:
            if secret:
                safe_item = safe_item.replace(secret, "***")
        safe_cmd.append(safe_item)
    printable = shlex.join(safe_cmd)
    print(f"+ {printable}", flush=True)
    try:
        subprocess.run([str(item) for item in cmd], cwd=cwd, env=env, check=True)
    except subprocess.CalledProcessError as exc:
        if secrets:
            raise RuntimeError(
                f"Command failed with exit code {exc.returncode}: {printable}"
            ) from None
        raise


def repo_dir_name(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    name = Path(path).name
    if name.endswith(".git"):
        name = name[:-4]
    if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
        raise ValueError(f"Unsafe repository directory name derived from {url!r}")
    return name


def validate_destination(destination: str, comfy_dir: Path) -> Path:
    dest = Path(destination)
    if not dest.is_absolute():
        dest = comfy_dir / dest
    resolved = dest.resolve()
    comfy_resolved = comfy_dir.resolve()
    if resolved != comfy_resolved and comfy_resolved not in resolved.parents:
        raise ValueError(f"Model destination escapes ComfyUI directory: {destination}")
    return resolved


def node_repository_url(node: dict) -> str:
    return node.get("reference") or (node.get("files") or [None])[0]


def install_node(
    node: dict, custom_nodes_dir: Path, update_nodes: bool
) -> dict[str, str]:
    repo_url = node_repository_url(node)
    name = repo_dir_name(repo_url)
    target = custom_nodes_dir / name
    pinned_commit = str(node.get("commit") or "").strip()

    if not target.exists():
        run(["git", "clone", "--depth", "1", repo_url, str(target)])
    elif not (target / ".git").exists():
        raise RuntimeError(
            f"Custom node path exists but is not a Git repository: {target}"
        )
    elif update_nodes and not pinned_commit:
        run(["git", "fetch", "--depth", "1", "origin"], cwd=target)
        run(["git", "reset", "--hard", "origin/HEAD"], cwd=target)
    else:
        print(f"Node already present, keeping installed revision: {target}")

    if pinned_commit:
        current_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=target, text=True
        ).strip()
        if current_commit != pinned_commit:
            run(["git", "fetch", "--depth", "1", "origin", pinned_commit], cwd=target)
            run(["git", "checkout", "--detach", pinned_commit], cwd=target)

    requirements = target / "requirements.txt"
    install_py = target / "install.py"
    pyproject = target / "pyproject.toml"
    setup_py = target / "setup.py"

    if requirements.exists():
        run([sys.executable, "-m", "pip", "install", "-r", str(requirements)])

    if install_py.exists():
        run([sys.executable, str(install_py)], cwd=target)
    elif (pyproject.exists() or setup_py.exists()) and not requirements.exists():
        # Some nodes are proper Python packages (for example gguf), while others
        # only use pyproject.toml for development tooling. A failed optional
        # editable install must not stop provisioning of the remaining nodes.
        try:
            run([sys.executable, "-m", "pip", "install", "-e", str(target)])
        except subprocess.CalledProcessError as exc:
            print(
                f"Warning: optional editable install failed for {target}: {exc} "
                "Keeping the cloned custom node and continuing.",
                flush=True,
            )

    commit = ""
    if (target / ".git").exists():
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=target, text=True
        ).strip()

    return {"repository": repo_url, "directory": str(target), "commit": commit}


def expected_bytes(model: dict) -> int | None:
    exact_value = model.get("sizeBytes")
    if exact_value is not None:
        try:
            return int(exact_value)
        except (TypeError, ValueError):
            return None

    # AI Launcher exports fileSize in MiB.
    value = model.get("fileSize")
    if value is None:
        return None
    try:
        return int(float(value) * 1024 * 1024)
    except (TypeError, ValueError):
        return None


def is_complete(path: Path, expected: int | None) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    if expected is None:
        return True
    # fileSize is exported as a floating-point MiB value. Allow only a small
    # rounding margin; the previous 5% margin could accept multi-GiB partials.
    return path.stat().st_size >= max(1, expected - 2 * 1024 * 1024)


def trusted_host(hostname: str, domain: str) -> bool:
    hostname = hostname.lower().rstrip(".")
    return hostname == domain or hostname.endswith(f".{domain}")


def add_query_parameter(url: str, key: str, value: str) -> str:
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    if not any(existing_key == key for existing_key, _ in query):
        query.append((key, value))
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )


def auth_provider(model: dict, url: str) -> str | None:
    configured = str(model.get("authProvider") or "").strip().lower()
    aliases = {
        "hf": "huggingface",
        "hugging-face": "huggingface",
        "civit-ai": "civitai",
    }
    configured = aliases.get(configured, configured)
    if configured:
        return configured

    hostname = (urlsplit(url).hostname or "").lower()
    if trusted_host(hostname, "huggingface.co"):
        return "huggingface"
    if trusted_host(hostname, "civitai.com"):
        return "civitai"
    return None


def truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def authenticated_download(model: dict) -> tuple[str, list[str], tuple[str, ...]]:
    url = model["url"]
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError(f"Unsupported model URL: {url!r}")

    hostname = parts.hostname.lower()
    provider = auth_provider(model, url)
    requires_auth = truthy(model.get("requiresAuth", False))
    hf_token = (
        os.getenv("HF_TOKEN", "").strip()
        or os.getenv("HUGGING_FACE_HUB_TOKEN", "").strip()
    )
    civitai_token = os.getenv("CIVITAI_TOKEN", "").strip()
    headers: list[str] = []
    secrets: list[str] = []

    if provider == "huggingface":
        if not trusted_host(hostname, "huggingface.co"):
            raise ValueError("Refusing to send HF_TOKEN to a non-Hugging Face host")
        if requires_auth and not hf_token:
            raise RuntimeError(
                f"Model {model.get('name') or url!r} requires the HF_TOKEN secret"
            )
        if hf_token:
            headers.append(f"Authorization: Bearer {hf_token}")
            secrets.append(hf_token)
    elif provider == "civitai":
        if not trusted_host(hostname, "civitai.com"):
            raise ValueError("Refusing to send CIVITAI_TOKEN to a non-Civitai host")
        if any(
            key.lower() == "token" and value
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ):
            raise ValueError(
                "Remove the Civitai token from the model URL and use the "
                "CIVITAI_TOKEN secret instead"
            )
        if requires_auth and not civitai_token:
            raise RuntimeError(
                f"Model {model.get('name') or url!r} requires the CIVITAI_TOKEN secret"
            )
        if civitai_token:
            url = add_query_parameter(url, "token", civitai_token)
            secrets.append(civitai_token)
    elif requires_auth:
        raise ValueError(
            f"Model {model.get('name') or url!r} requires authentication, but "
            "authProvider is not huggingface or civitai"
        )

    return url, headers, tuple(secrets)


def download_model(model: dict, comfy_dir: Path) -> dict[str, object]:
    source_url = model["url"]
    filename = model.get("customFilename") or Path(urlparse(source_url).path).name
    destination = validate_destination(model["destinationPath"], comfy_dir)
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / filename
    expected = expected_bytes(model)

    if is_complete(output, expected):
        print(f"Model already present: {output}")
        return {
            "url": source_url,
            "path": str(output),
            "bytes": output.stat().st_size,
            "status": "already-present",
        }

    url, headers, secrets = authenticated_download(model)
    aria = shutil.which("aria2c")

    if aria:
        cmd = [
            aria,
            "--continue=true",
            "--max-connection-per-server=8",
            "--split=8",
            "--min-split-size=10M",
            "--file-allocation=none",
            "--auto-file-renaming=false",
            "--allow-overwrite=true",
            "--max-tries=10",
            "--retry-wait=5",
            "--timeout=60",
            "--console-log-level=notice",
            "--dir", str(destination),
            "--out", filename,
        ]
        for header in headers:
            cmd.append(f"--header={header}")
        cmd.append(url)
    else:
        cmd = [
            "curl", "-fL", "--retry", "10", "--retry-delay", "5",
            "--continue-at", "-", "--output", str(output),
        ]
        for header in headers:
            cmd.extend(["-H", header])
        cmd.append(url)

    run(cmd, secrets=secrets)

    if not is_complete(output, expected):
        actual = output.stat().st_size if output.exists() else 0
        raise RuntimeError(
            f"Downloaded file appears incomplete: {output}; "
            f"actual={actual}, expected≈{expected}"
        )

    return {
        "url": source_url,
        "path": str(output),
        "bytes": output.stat().st_size,
        "status": "downloaded",
    }


def validate_config(config: dict) -> None:
    required = ["name", "comfyuiVersion", "models", "customNodes"]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Config is missing keys: {', '.join(missing)}")

    comfyui_version = str(config["comfyuiVersion"])
    if (
        not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", comfyui_version)
        or ".." in comfyui_version
    ):
        raise ValueError("comfyuiVersion must be a safe Git ref")

    for index, model in enumerate(config["models"]):
        for key in ("url", "destinationPath"):
            if not model.get(key):
                raise ValueError(f"models[{index}] is missing {key}")
        parts = urlsplit(model["url"])
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            raise ValueError(f"models[{index}].url must be an HTTP(S) URL")
        filename = model.get("customFilename")
        if filename and Path(filename).name != filename:
            raise ValueError(f"models[{index}].customFilename must be a file name")
        provider = auth_provider(model, model["url"])
        if provider not in {None, "huggingface", "civitai"}:
            raise ValueError(
                f"models[{index}].authProvider must be huggingface or civitai"
            )

    for index, node in enumerate(config["customNodes"]):
        url = node_repository_url(node)
        if not url:
            raise ValueError(f"customNodes[{index}] has no repository URL")
        commit = str(node.get("commit") or "").strip()
        if commit and not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
            raise ValueError(
                f"customNodes[{index}].commit must be a full 40-character SHA"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--comfy-dir", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    validate_config(config)

    model_bytes = sum(expected_bytes(model) or 0 for model in config["models"])
    model_gib = model_bytes / (1024**3)
    print(
        f"Profile={config['name']!r}; ComfyUI={config['comfyuiVersion']}; "
        f"models={len(config['models'])}; nodes={len(config['customNodes'])}; "
        f"model data≈{model_gib:.1f} GiB"
    )

    if args.validate_only:
        return 0

    comfy_dir = args.comfy_dir.resolve()
    custom_nodes_dir = comfy_dir / "custom_nodes"
    custom_nodes_dir.mkdir(parents=True, exist_ok=True)

    update_nodes = os.getenv("UPDATE_NODES", "0") == "1"
    node_results = []
    seen_repos: set[str] = set()

    for node in config["customNodes"]:
        repo_url = node_repository_url(node)
        if repo_url in seen_repos:
            print(f"Skipping duplicate node repository: {repo_url}")
            continue
        seen_repos.add(repo_url)
        node_results.append(install_node(node, custom_nodes_dir, update_nodes))

    model_results = []
    for position, model in enumerate(config["models"], start=1):
        print(
            f"=== Model {position}/{len(config['models'])}: "
            f"{model.get('customFilename') or model.get('name')} ==="
        )
        model_results.append(download_model(model, comfy_dir))

    default_state_dir = Path(os.getenv("WORKSPACE", "/workspace")) / "comfyui-cloud"
    state_dir = Path(os.getenv("STATE_DIR", str(default_state_dir)))
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "profile": config["name"],
        "comfyuiVersion": config["comfyuiVersion"],
        "nodes": node_results,
        "models": model_results,
    }
    (state_dir / "install-state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (state_dir / "INSTALL_COMPLETE").write_text("ok\n", encoding="utf-8")
    print("All configured nodes and models are installed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
