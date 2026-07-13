# Vast.ai — Image template

- Name: `ComfyUI Image Production`
- Launch mode: `Jupyter + SSH`
- Port: `8188/tcp`
- Disk: `220 GB`
- Visibility: `Private`
- Recommended VRAM: `48 GB+`

## Environment variables

```text
PROVISIONING_SCRIPT=https://raw.githubusercontent.com/<GITHUB_USERNAME>/comfyui-cloud-templates/main/providers/vastai/provision.sh
REPO_RAW_BASE=https://raw.githubusercontent.com/<GITHUB_USERNAME>/comfyui-cloud-templates/main
CONFIG_URL=https://raw.githubusercontent.com/<GITHUB_USERNAME>/comfyui-cloud-templates/main/configs/image.json
COMFY_VERSION=v0.27.0
COMFY_PORT=8188
PORTAL_CONFIG=localhost:8188:8188:/:ComfyUI
```

## On-start script

```bash
if [[ -x /workspace/comfyui-cloud/runtime/start-comfyui.sh ]]; then
  /workspace/comfyui-cloud/runtime/start-comfyui.sh
fi
```
