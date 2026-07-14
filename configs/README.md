# Формат профиля

Минимальная структура:

```json
{
  "name": "product-photo",
  "comfyuiVersion": "v0.27.0",
  "models": [],
  "customNodes": []
}
```

## Публичная Hugging Face модель

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

`fileSize` задаётся в MiB. Если известен точный размер, вместо него можно
добавить `sizeBytes`.

## Закрытая или gated Hugging Face модель

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

Нужен секрет `HF_TOKEN`. Аккаунт токена должен иметь доступ к репозиторию.

## Закрытая Civitai модель

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

Нужен секрет `CIVITAI_TOKEN`. Установщик добавит его только к запросу на
доверенный домен Civitai и скроет значение в логах.

## Custom node

```json
{
  "title": "Example node",
  "reference": "https://github.com/owner/repository",
  "files": ["https://github.com/owner/repository"]
}
```

Для воспроизводимой установки можно закрепить commit:

```json
{
  "title": "Example node",
  "reference": "https://github.com/owner/repository",
  "files": ["https://github.com/owner/repository"],
  "commit": "FULL_40_CHARACTER_COMMIT_SHA"
}
```

Зависимости устанавливаются в следующем порядке:

1. `requirements.txt`, если он есть;
2. `install.py`, если он есть;
3. необязательный `pip install -e`, только если остались `pyproject.toml` или
   `setup.py` без двух предыдущих установщиков.

Ошибка третьего необязательного шага не останавливает остальные ноды и модели.
