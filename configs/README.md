# Profile schema

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
