# RunPod — Image template

- Name: `ComfyUI Image Production`
- Container image: `ghcr.io/<GITHUB_USERNAME>/comfyui-cloud:0.1.0`
- Container disk: `30 GB`
- Volume/Network Volume: `220 GB`
- Mount path: `/workspace`
- HTTP port: `8188`
- Recommended VRAM: `48 GB+`

## Environment variables

```text
PROFILE=image
REPO_RAW_BASE=https://raw.githubusercontent.com/<GITHUB_USERNAME>/comfyui-cloud-templates/main
COMFY_VERSION=v0.27.0
COMFY_PORT=8188
```
