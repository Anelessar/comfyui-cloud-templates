# Vast.ai Image Family Template

Base every image-family template on the official Vast.ai ComfyUI template.
The settings below intentionally follow the official template's Supervisor,
Caddy, Jupyter, and Instance Portal architecture.

## Base image and launch mode

```text
Image: vastai/comfy:v0.27.0-cuda-13.2-py312
Launch mode: Jupyter + SSH
On-start script: entrypoint.sh
Jupyter direct HTTPS: enabled
Visibility: Private
```

Do not start ComfyUI from the custom provisioning script. The official image
manages it through Supervisor and starts it on internal port `18188` after
first-boot provisioning releases the service.

## Docker ports

Keep these official ports:

```text
1111/tcp
8080/tcp
8384/tcp
72299/tcp
8188/tcp
```

The public ComfyUI port is `8188`; Caddy proxies it to the Supervisor-managed
ComfyUI process on internal port `18188`.

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
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/qwen-image.json
```

Create one private template per family and change only the template name,
recommended disk size, and `CONFIG_URL`:

| Template | Profile | Recommended disk |
|---|---|---:|
| ComfyUI Qwen Image | `qwen-image.json` | 100 GB |
| ComfyUI FLUX | `flux.json` | 70 GB |
| ComfyUI Z-Image | `z-image.json` | 60 GB |
| ComfyUI Krea 2 | `krea-2.json` | 70 GB |

## Account secrets

Store these once under Vast.ai account environment variables, not inside a
template or repository:

```text
HF_TOKEN
CIVITAI_TOKEN
```

The provisioning installer automatically uses them for authenticated model
downloads and redacts them from command logs.

## Runtime behavior

The official image prepares `/workspace/ComfyUI` and keeps its ComfyUI service
paused while provisioning is active. The custom script validates the selected
profile and installs its nodes synchronously. Model downloads are then launched
in the background, provisioning exits, and the official Supervisor service
starts ComfyUI. This keeps the working official portal route while avoiding a
second competing ComfyUI process.

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
tail -f /workspace/comfyui-cloud/logs/models.log
bash /workspace/comfyui-cloud/runtime/check-install.sh
```
