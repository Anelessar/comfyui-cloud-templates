# ComfyUI Cloud Templates

Один репозиторий для Vast.ai и RunPod.

- Image: 16 моделей, 14 наборов custom nodes, около 126.0 GiB моделей.
- Video: 15 моделей, 15 наборов custom nodes, около 95.3 GiB моделей.
- ComfyUI: `v0.27.0`.

## Структура

```text
comfyui-cloud-templates/
├── configs/
├── common/
├── providers/vastai/
├── providers/runpod/
└── .github/workflows/build-runpod-image.yml
```

## Подготовка

Глобально замени `<GITHUB_USERNAME>` на свой GitHub username и загрузи папку в repository `comfyui-cloud-templates`.

## Vast.ai

Используй инструкции `providers/vastai/image-template.md` и `providers/vastai/video-template.md`.

## RunPod

GitHub Actions собирает общий image `ghcr.io/<GITHUB_USERNAME>/comfyui-cloud:0.1.0`. Затем создай два RunPod templates по файлам в `providers/runpod/`. Различие между ними — `PROFILE=image` и `PROFILE=video`.

## Модели

Модели не встроены в Docker image. Они устанавливаются в `/workspace` и сохраняются на подключённом volume. Для RunPod рекомендуется отдельный Network Volume для Image и Video.

## Проверка

Vast.ai:
```bash
bash /workspace/comfyui-cloud/runtime/check-install.sh
```

RunPod:
```bash
bash /opt/comfyui-cloud/common/check-install.sh
```

Логи:
```bash
tail -f /workspace/comfyui-cloud/logs/comfyui.log
```
