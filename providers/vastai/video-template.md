# Vast.ai — Video template

Copy the working Image template. Do not change its Docker image, launch mode,
`PORTAL_CONFIG`, standard variables, Jupyter/SSH ports, or on-start script.

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
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/wan22-animate.json
```

Copy the template for another video workflow and change only its name, disk
size, GPU filters, and `CONFIG_URL` profile filename.

For direct external access, optionally add `8188/tcp`. Otherwise use an SSH
tunnel without changing the portal configuration:

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

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
bash /workspace/comfyui-cloud/runtime/check-install.sh
```
