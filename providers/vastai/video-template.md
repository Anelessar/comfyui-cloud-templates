# Vast.ai Wan Video Family Template

Use the same official settings as the image-family templates:

```text
Image: vastai/comfy:v0.27.0-cuda-13.2-py312
Launch mode: Jupyter + SSH
On-start script: entrypoint.sh
Jupyter direct HTTPS: enabled
Visibility: Private
Recommended disk: 150 GB
```

## Docker ports

```text
1111/tcp
8080/tcp
8384/tcp
72299/tcp
8188/tcp
```

## Environment variables

```text
COMFYUI_ARGS=--disable-auto-launch --disable-xformers --port 18188 --enable-cors-header
PORTAL_CONFIG=localhost:1111:11111:/:Instance Portal|localhost:8188:18188:/:ComfyUI|localhost:8080:18080:/:Jupyter|localhost:8080:8080:/terminals/1:Jupyter Terminal|localhost:8384:18384:/:Syncthing
OPEN_BUTTON_PORT=1111
OPEN_BUTTON_TOKEN=1
JUPYTER_DIR=/
DATA_DIRECTORY=/workspace/
PROVISIONING_SCRIPT=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/providers/vastai/provision.sh
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/wan-video.json
```

The external ComfyUI application port is `8188`; the official Caddy proxy sends
traffic to ComfyUI on internal port `18188`. Do not start another process on
`8188` and do not replace `entrypoint.sh`.

Store `HF_TOKEN` and `CIVITAI_TOKEN` once as Vast.ai account environment
variables. Never put their values in this file, a profile JSON, or the template.

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
tail -f /workspace/comfyui-cloud/logs/models.log
bash /workspace/comfyui-cloud/runtime/check-install.sh
```
