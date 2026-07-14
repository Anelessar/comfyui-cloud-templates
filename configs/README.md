# Profile schema

Ready-to-use workflow profiles are listed in `configs/profiles/README.md`. The
top-level `image.json` and `video.json` files are retained as the original full
AI Launcher exports, not as recommended disposable-instance profiles.

Minimal structure:

```json
{
  "name": "product-photo",
  "comfyuiVersion": "v0.27.0",
  "models": [],
  "customNodes": []
}
```

## Public Hugging Face model

```json
{
  "name": "owner/repository - model.safetensors",
  "url": "https://huggingface.co/owner/repository/resolve/main/model.safetensors",
  "destinationPath": "/workspace/ComfyUI/models/checkpoints",
  "customFilename": "model.safetensors",
  "fileSize": 1024.0,
  "requiresAuth": false
}
```

`fileSize` is expressed in MiB. If the exact size is known, use `sizeBytes`.

## Private or gated Hugging Face model

```json
{
  "name": "owner/private-repository - model.safetensors",
  "url": "https://huggingface.co/owner/private-repository/resolve/main/model.safetensors",
  "destinationPath": "/workspace/ComfyUI/models/checkpoints",
  "customFilename": "model.safetensors",
  "fileSize": 1024.0,
  "requiresAuth": true,
  "authProvider": "huggingface"
}
```

This requires the `HF_TOKEN` secret. The token's account must have repository
access.

## Private Civitai model

```json
{
  "name": "Civitai model version 123456",
  "url": "https://civitai.com/api/download/models/123456",
  "destinationPath": "/workspace/ComfyUI/models/checkpoints",
  "customFilename": "model.safetensors",
  "fileSize": 1024.0,
  "requiresAuth": true,
  "authProvider": "civitai"
}
```

This requires the `CIVITAI_TOKEN` secret. The installer sends it only to the
trusted Civitai domain and redacts it from logs.

## Custom node

```json
{
  "title": "Example node",
  "reference": "https://github.com/owner/repository",
  "files": ["https://github.com/owner/repository"]
}
```

For reproducible installation, pin a full commit SHA:

```json
{
  "title": "Example node",
  "reference": "https://github.com/owner/repository",
  "files": ["https://github.com/owner/repository"],
  "commit": "FULL_40_CHARACTER_COMMIT_SHA"
}
```

Dependencies are installed in this order:

1. `requirements.txt`, when present.
2. `install.py`, when present.
3. Optional `pip install -e` when only `pyproject.toml` or `setup.py` remains.

A failure in the third optional step does not stop other nodes or models.

## Build a profile from an export

List the selectable entries:

```bash
python3 tools/profile_builder.py list configs/image.json
```

The command prints one-based model and custom-node numbers. Create a profile by
selecting complete dependencies for one workflow:

```bash
python3 tools/profile_builder.py create \
  configs/image.json \
  configs/profiles/my-workflow.json \
  --name my-workflow \
  --models 1,2,3,4 \
  --nodes 10 \
  --with-discovery-tools
```

`--with-discovery-tools` adds ComfyUI Manager and ComfyUI Hugging Face
Downloader when the source export contains them. It does not guess model
dependencies. A LoRA, text encoder, VAE, or high/low-noise expert must stay with
the base models required by the workflow.

Validate the result before pushing it:

```bash
python3 common/install_from_config.py \
  --config configs/profiles/my-workflow.json \
  --comfy-dir /workspace/ComfyUI \
  --validate-only
```
