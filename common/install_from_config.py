#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    printable = " ".join(cmd)
    print(f"+ {printable}", flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


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


def install_node(repo_url: str, custom_nodes_dir: Path, update_nodes: bool) -> dict[str, str]:
    name = repo_dir_name(repo_url)
    target = custom_nodes_dir / name

    if not target.exists():
        run(["git", "clone", "--depth", "1", repo_url, str(target)])
    elif (target / ".git").exists() and update_nodes:
        run(["git", "fetch", "--depth", "1", "origin"], cwd=target)
        run(["git", "reset", "--hard", "origin/HEAD"], cwd=target)
    else:
        print(f"Node already present, keeping installed revision: {target}")

    requirements = target / "requirements.txt"
    install_py = target / "install.py"
    pyproject = target / "pyproject.toml"
    setup_py = target / "setup.py"

    if requirements.exists():
        run([sys.executable, "-m", "pip", "install", "-r", str(requirements)])

    if install_py.exists():
        run([sys.executable, str(install_py)], cwd=target)
    elif (pyproject.exists() or setup_py.exists()) and not requirements.exists():
        # Some custom nodes declare dependencies only through package metadata.
        run([sys.executable, "-m", "pip", "install", "-e", str(target)])

    commit = ""
    if (target / ".git").exists():
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=target, text=True
        ).strip()

    return {"repository": repo_url, "directory": str(target), "commit": commit}


def expected_bytes(model: dict) -> int | None:
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
    # Allow metadata rounding and small upstream revisions.
    return path.stat().st_size >= int(expected * 0.95)


def download_model(model: dict, comfy_dir: Path) -> dict[str, object]:
    url = model["url"]
    filename = model.get("customFilename") or Path(urlparse(url).path).name
    destination = validate_destination(model["destinationPath"], comfy_dir)
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / filename
    expected = expected_bytes(model)

    if is_complete(output, expected):
        print(f"Model already present: {output}")
        return {
            "url": url,
            "path": str(output),
            "bytes": output.stat().st_size,
            "status": "already-present",
        }

    aria = shutil.which("aria2c")
    token = os.getenv("HF_TOKEN", "").strip()

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
        if token and "huggingface.co" in url:
            cmd.append(f"--header=Authorization: Bearer {token}")
        cmd.append(url)
    else:
        cmd = [
            "curl", "-fL", "--retry", "10", "--retry-delay", "5",
            "--continue-at", "-", "--output", str(output),
        ]
        if token and "huggingface.co" in url:
            cmd.extend(["-H", f"Authorization: Bearer {token}"])
        cmd.append(url)

    run(cmd)

    if not is_complete(output, expected):
        actual = output.stat().st_size if output.exists() else 0
        raise RuntimeError(
            f"Downloaded file appears incomplete: {output}; "
            f"actual={actual}, expected≈{expected}"
        )

    return {
        "url": url,
        "path": str(output),
        "bytes": output.stat().st_size,
        "status": "downloaded",
    }


def validate_config(config: dict) -> None:
    required = ["name", "comfyuiVersion", "models", "customNodes"]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Config is missing keys: {', '.join(missing)}")

    for index, model in enumerate(config["models"]):
        for key in ("url", "destinationPath"):
            if not model.get(key):
                raise ValueError(f"models[{index}] is missing {key}")

    for index, node in enumerate(config["customNodes"]):
        url = node.get("reference") or (node.get("files") or [None])[0]
        if not url:
            raise ValueError(f"customNodes[{index}] has no repository URL")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--comfy-dir", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    validate_config(config)

    model_gib = sum(float(m.get("fileSize", 0)) for m in config["models"]) / 1024
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
        repo_url = node.get("reference") or node["files"][0]
        if repo_url in seen_repos:
            print(f"Skipping duplicate node repository: {repo_url}")
            continue
        seen_repos.add(repo_url)
        node_results.append(install_node(repo_url, custom_nodes_dir, update_nodes))

    model_results = []
    for position, model in enumerate(config["models"], start=1):
        print(
            f"=== Model {position}/{len(config['models'])}: "
            f"{model.get('customFilename') or model.get('name')} ==="
        )
        model_results.append(download_model(model, comfy_dir))

    state_dir = Path(os.getenv("STATE_DIR", str(Path(os.getenv("WORKSPACE", "/workspace")) / "comfyui-cloud")))
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
