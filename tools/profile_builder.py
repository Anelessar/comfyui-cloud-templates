#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DISCOVERY_REPOSITORIES = {
    "https://github.com/jnxmx/ComfyUI_HuggingFace_Downloader",
    "https://github.com/ltdrdata/ComfyUI-Manager",
}


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    for key in ("name", "comfyuiVersion", "models", "customNodes"):
        if key not in config:
            raise ValueError(f"{path} is missing {key}")
    return config


def parse_indices(value: str, length: int, label: str) -> list[int]:
    if not value.strip():
        return []

    result: list[int] = []
    seen: set[int] = set()
    for raw_part in value.split(","):
        part = raw_part.strip()
        if not re.fullmatch(r"[0-9]+", part):
            raise ValueError(f"Invalid {label} index: {part!r}")
        one_based = int(part)
        if not 1 <= one_based <= length:
            raise ValueError(
                f"{label} index {one_based} is outside the valid range 1..{length}"
            )
        zero_based = one_based - 1
        if zero_based not in seen:
            seen.add(zero_based)
            result.append(zero_based)
    return result


def repository_url(node: dict) -> str:
    return str(node.get("reference") or (node.get("files") or [""])[0])


def file_size_gib(model: dict) -> float:
    if model.get("sizeBytes") is not None:
        return int(model["sizeBytes"]) / (1024**3)
    return float(model.get("fileSize") or 0) / 1024


def list_config(config: dict) -> None:
    print("Models")
    for index, model in enumerate(config["models"], start=1):
        filename = model.get("customFilename") or model.get("name") or model["url"]
        print(f"  {index:>2}. {file_size_gib(model):>6.1f} GiB  {filename}")

    print("\nCustom nodes")
    for index, node in enumerate(config["customNodes"], start=1):
        title = node.get("title") or repository_url(node)
        print(f"  {index:>2}. {title}")


def build_profile(
    source: dict,
    name: str,
    model_indices: list[int],
    node_indices: list[int],
    include_discovery: bool,
) -> dict:
    selected_nodes = [source["customNodes"][index] for index in node_indices]
    if include_discovery:
        selected_repositories = {repository_url(node) for node in selected_nodes}
        for node in source["customNodes"]:
            repository = repository_url(node)
            if (
                repository in DISCOVERY_REPOSITORIES
                and repository not in selected_repositories
            ):
                selected_nodes.append(node)
                selected_repositories.add(repository)

    return {
        "name": name,
        "comfyuiVersion": source["comfyuiVersion"],
        "models": [source["models"][index] for index in model_indices],
        "customNodes": selected_nodes,
    }


def write_profile(profile: dict, output: Path, force: bool) -> None:
    if output.exists() and not force:
        raise FileExistsError(f"{output} already exists; pass --force to replace it")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a small workflow profile from an AI Launcher export."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List selectable models and nodes")
    list_parser.add_argument("source", type=Path)

    create_parser = subparsers.add_parser("create", help="Create a selected profile")
    create_parser.add_argument("source", type=Path)
    create_parser.add_argument("output", type=Path)
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument(
        "--models", required=True, help="Comma-separated one-based model indices"
    )
    create_parser.add_argument(
        "--nodes", default="", help="Comma-separated one-based custom-node indices"
    )
    create_parser.add_argument(
        "--with-discovery-tools",
        action="store_true",
        help="Include ComfyUI Manager and Hugging Face Downloader when available",
    )
    create_parser.add_argument("--force", action="store_true")

    args = parser.parse_args()
    source = load_config(args.source)

    if args.command == "list":
        list_config(source)
        return 0

    model_indices = parse_indices(args.models, len(source["models"]), "model")
    node_indices = parse_indices(args.nodes, len(source["customNodes"]), "node")
    profile = build_profile(
        source,
        args.name,
        model_indices,
        node_indices,
        args.with_discovery_tools,
    )
    write_profile(profile, args.output, args.force)
    model_gib = sum(file_size_gib(model) for model in profile["models"])
    print(
        f"Created {args.output}: {len(profile['models'])} models, "
        f"{len(profile['customNodes'])} nodes, approximately {model_gib:.1f} GiB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
