# RunPod — Video template

- Name: `ComfyUI Video Production`.
- Container image: `ghcr.io/anelessar/comfyui-cloud:latest`.
- Container start command: leave empty.
- Container disk: model data from `configs/video.json` plus at least 50 GB.
- Volume/Network Volume: `0 GB` for disposable instances.
- HTTP port: `8188`.
- Visibility: `Private`.

## Environment variables

```text
PROFILE=video
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
HF_TOKEN={{ RUNPOD_SECRET_huggingface_token }}
CIVITAI_TOKEN={{ RUNPOD_SECRET_civitai_token }}
```

Secret variables can be omitted when the profile contains only public models.
For an additional workflow, set its direct `CONFIG_URL` instead of `PROFILE`.
