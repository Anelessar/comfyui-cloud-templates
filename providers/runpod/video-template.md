# RunPod — Video template

- Name: `ComfyUI Video Production`
- Container image: `ghcr.io/<GITHUB_USERNAME>/comfyui-cloud:0.1.0`
- Container disk: `30 GB`
- Volume/Network Volume: `250 GB`
- Mount path: `/workspace`
- HTTP port: `8188`
- Recommended VRAM: `48 GB+`; `80 GB` preferred

## Environment variables

```text
PROFILE=video
REPO_RAW_BASE=https://raw.githubusercontent.com/<GITHUB_USERNAME>/comfyui-cloud-templates/main
COMFY_VERSION=v0.27.0
COMFY_PORT=8188
```
