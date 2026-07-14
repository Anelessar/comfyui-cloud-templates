# RunPod — Video template

- Name: `ComfyUI Video Production`;
- Container image: `ghcr.io/anelessar/comfyui-cloud:latest`;
- Container start command: оставить пустым;
- Container disk: объём моделей из `configs/video.json` плюс минимум 50 GB;
- Volume/Network Volume: `0 GB`, если instance каждый раз удаляется;
- HTTP port: `8188`;
- Visibility: `Private`.

## Environment variables

```text
PROFILE=video
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
HF_TOKEN={{ RUNPOD_SECRET_huggingface_token }}
CIVITAI_TOKEN={{ RUNPOD_SECRET_civitai_token }}
```

Секретные переменные можно пропустить, если профиль содержит только публичные
модели. Для дополнительного workflow вместо `PROFILE` задай его `CONFIG_URL`.
