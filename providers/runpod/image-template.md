# RunPod — Image template

- Name: `ComfyUI Image Production`;
- Container image: `ghcr.io/anelessar/comfyui-cloud:latest`;
- Container start command: оставить пустым;
- Container disk: объём моделей из `configs/image.json` плюс минимум 40 GB;
- Volume/Network Volume: `0 GB`, если instance каждый раз удаляется;
- HTTP port: `8188`;
- Visibility: `Private`.

## Environment variables

```text
PROFILE=image
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
```

Можно вместо `PROFILE` задать прямой `CONFIG_URL` на любой новый профиль.
`COMFY_VERSION` и `COMFY_PORT` не нужны.

## Секреты RunPod

Создай secrets `huggingface_token` и `civitai_token`, затем добавь в template:

```text
HF_TOKEN={{ RUNPOD_SECRET_huggingface_token }}
CIVITAI_TOKEN={{ RUNPOD_SECRET_civitai_token }}
```

Если закрытых моделей у провайдера нет, его переменную можно не добавлять.
