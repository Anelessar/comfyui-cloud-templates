# Vast.ai — Image template

Этот шаблон создаётся как копия официального PyTorch template, который уже
открывает Jupyter на выбранной машине.

## Что оставить без изменений

- Docker image официального PyTorch template;
- Launch mode: `Jupyter + SSH`;
- исходные `PORTAL_CONFIG`, `OPEN_BUTTON_*`, `JUPYTER_DIR` и `DATA_DIRECTORY`;
- исходный On-start Script;
- стандартные порты Jupyter и SSH.

Не добавляй ComfyUI в `PORTAL_CONFIG` и не заменяй On-start Script. Именно эти
изменения раньше ломали внешний доступ к работающему Jupyter.

## Настройки профиля

- Name: `ComfyUI Image Production`;
- Visibility: `Private`;
- Disk: объём моделей из `configs/image.json` плюс минимум 40 GB;
- GPU: подбирается под конкретный уменьшенный workflow;
- Port: `8188/tcp` — добавь только для прямого внешнего доступа к ComfyUI.

Без отдельного порта UI всегда можно открыть через SSH tunnel:

```bash
ssh -p SSH_PORT root@HOST -L 8188:localhost:8188
```

Затем открыть `http://127.0.0.1:8188` на своём компьютере.

## Три новые переменные template

```text
PROVISIONING_SCRIPT=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/providers/vastai/provision.sh
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/image.json
```

`COMFY_VERSION` и `COMFY_PORT` добавлять не нужно. Версия читается из
`comfyuiVersion` выбранного JSON, порт по умолчанию равен `8188`.

При стандартных пяти переменных официального PyTorch template итоговый набор
укладывается ровно в лимит 10:

```text
5 стандартных + PROVISIONING_SCRIPT + REPO_RAW_BASE + CONFIG_URL
+ HF_TOKEN + CIVITAI_TOKEN = 10
```

## Секреты аккаунта Vast.ai

В `Account → Environment Variables` создай две зашифрованные переменные:

```text
HF_TOKEN=hf_...
CIVITAI_TOKEN=...
```

Не записывай значения токенов в template, GitHub или JSON. Account-level
variables автоматически доступны запущенному instance. Если закрытых моделей
нет, соответствующий секрет можно не создавать.

## Проверка

Jupyter должен открыться как у исходного официального template. Установка идёт
в фоне платформенного provisioning-процесса; её лог:

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
```

После завершения:

```bash
bash /workspace/comfyui-cloud/runtime/check-install.sh
```
