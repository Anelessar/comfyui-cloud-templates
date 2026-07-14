# ComfyUI Cloud Templates

Один установщик для Vast.ai и RunPod. Набор моделей и custom nodes задаётся
только JSON-профилем в `configs/`.

## Что было исправлено

- Vast.ai больше не требует изменения `PORTAL_CONFIG` или On-start Script;
- ошибка необязательного `pip install -e` отдельной ноды не останавливает всё;
- `comfyuiVersion` читается из выбранного JSON, а не зашит в shell-скрипт;
- поддержаны закрытые модели Hugging Face и Civitai;
- `HF_TOKEN` и `CIVITAI_TOKEN` маскируются в командах и ошибках;
- частично загруженные файлы продолжаются через `aria2c`;
- готовая модель пропускается с более строгой проверкой размера;
- custom node можно закрепить полем `commit`.

## Что менять для нового workflow

Создай или замени один файл, например:

```text
configs/product-photo.json
```

В нём оставь только модели и ноды этого workflow. Полный формат и примеры
закрытых моделей описаны в `configs/README.md`.

Далее меняется только `CONFIG_URL`:

```text
https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/product-photo.json
```

Скрипты провайдера менять не нужно.

Текущие `image.json` и `video.json` сохранены без сокращения. Они всё ещё очень
большие; перед регулярной арендой новых GPU их нужно разделить по workflow.
Токен не ускорит передачу десятков гигабайт — реальное ускорение даёт только
уменьшение профиля.

## Vast.ai

Используй:

- `providers/vastai/image-template.md`;
- `providers/vastai/video-template.md`.

Главное правило: копируй рабочий официальный PyTorch template и не меняй его
`PORTAL_CONFIG`, On-start Script, Jupyter и SSH. Добавляются только три URL
переменные. Токены создаются отдельно в account-level Environment Variables.

## RunPod

GitHub Actions собирает общий образ:

```text
ghcr.io/anelessar/comfyui-cloud:latest
```

Настройки находятся в:

- `providers/runpod/image-template.md`;
- `providers/runpod/video-template.md`.

Для одноразовых Pods без платного постоянного хранилища поставь Volume в `0 GB`,
а Container disk рассчитай как размер моделей профиля плюс 40–50 GB.

## Логи и проверка

Vast.ai:

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
bash /workspace/comfyui-cloud/runtime/check-install.sh
```

RunPod:

```bash
bash /opt/comfyui-cloud/common/check-install.sh
```

Лог ComfyUI:

```bash
tail -f /workspace/comfyui-cloud/logs/comfyui.log
```

## Секреты

Никогда не добавляй настоящие значения в GitHub, JSON или обычный текст
template. Нужные имена переменных:

```text
HF_TOKEN
CIVITAI_TOKEN
```

Для gated Hugging Face-модели одного токена недостаточно: аккаунт, которому
принадлежит токен, должен предварительно получить доступ или принять лицензию.
