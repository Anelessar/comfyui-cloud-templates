# Vast.ai — Video template

Copy the working Image template. Do not change its Docker image, launch mode,
standard variables, Jupyter/SSH ports, on-start script, exposed ComfyUI port, or
the ComfyUI entry already appended to `PORTAL_CONFIG`:

```text
|localhost:8188:8188:/:ComfyUI
```

The provisioning script stores the Vast-specific IPv6 listen address in
`/workspace/comfyui-cloud/comfy-listen-host`. This is required because current
Vast PyTorch images resolve the Cloudflare tunnel target `localhost` to `::1`.

Change only:

- Name: `ComfyUI Video Production`.
- Disk: model data from the selected `configs/profiles/*.json` file plus at
  least 50 GB.
- GPU: select according to the reduced video workflow's requirements.
- `CONFIG_URL`: use the value below.

## Three new template variables

```text
PROVISIONING_SCRIPT=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/providers/vastai/provision.sh
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/wan-video.json
```

Copy the template for another video family and change only its name, disk size,
GPU filters, and `CONFIG_URL` profile filename.

Keep `8188/tcp` exposed so the application card can reach ComfyUI. An SSH
tunnel remains available as a fallback:

```bash
ssh -p SSH_PORT root@HOST -L 8188:localhost:8188
```

## Secrets

Create these once under `Account → Environment Variables`:

```text
HF_TOKEN=hf_...
CIVITAI_TOKEN=...
```

They are shared by Image and Video instances. Do not duplicate secret values in
the template.

## Validation

The ComfyUI application card is present immediately on a newly created
instance, but it becomes usable only after provisioning starts ComfyUI on port
`8188`. Existing instances are not modified retroactively.

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
bash /workspace/comfyui-cloud/runtime/check-install.sh
```
