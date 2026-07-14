# RunPod — Image template

- Name: `ComfyUI Image Production`.
- Container image: `ghcr.io/anelessar/comfyui-cloud:latest`.
- Container start command: leave empty.
- Container disk: model data from the selected profile plus at least 40 GB.
- Volume/Network Volume: `0 GB` for disposable instances.
- HTTP port: `8188`.
- Visibility: `Private`.

## Environment variables

```text
PROFILE=qwen-image
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
```

Set `PROFILE` to any filename under `configs/profiles/` without `.json`. A direct
`CONFIG_URL` is also supported. `COMFY_VERSION` and `COMFY_PORT` are not
required.

## RunPod secrets

Create `huggingface_token` and `civitai_token` secrets, then add:

```text
HF_TOKEN={{ RUNPOD_SECRET_huggingface_token }}
CIVITAI_TOKEN={{ RUNPOD_SECRET_civitai_token }}
```

Omit a provider's variable when the selected profile contains only public
models from that provider.
