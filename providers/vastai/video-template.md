# Vast.ai — Video template

Создай копию рабочего Image template. Не меняй Docker image, Launch mode,
`PORTAL_CONFIG`, стандартные переменные, порты Jupyter/SSH и On-start Script.

Измени только:

- Name: `ComfyUI Video Production`;
- Disk: объём моделей из `configs/video.json` плюс минимум 50 GB;
- GPU: под требования конкретного уменьшенного video workflow;
- `CONFIG_URL` — значение ниже.

## Три новые переменные template

```text
PROVISIONING_SCRIPT=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/providers/vastai/provision.sh
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/video.json
```

Для прямого внешнего доступа можно добавить `8188/tcp`. Альтернатива без
изменения portal-конфигурации:

```bash
ssh -p SSH_PORT root@HOST -L 8188:localhost:8188
```

## Секреты

Один раз создай в `Account → Environment Variables`:

```text
HF_TOKEN=hf_...
CIVITAI_TOKEN=...
```

Они общие для Image и Video instances. Не дублируй секреты в template.

## Проверка

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
bash /workspace/comfyui-cloud/runtime/check-install.sh
```
