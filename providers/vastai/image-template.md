# Vast.ai — Image template

Create this template by copying an official PyTorch template that already opens
Jupyter successfully on a selected machine.

## Keep unchanged

- The official PyTorch Docker image.
- Launch mode: `Jupyter + SSH`.
- Existing `PORTAL_CONFIG` application entries, `OPEN_BUTTON_*`, `JUPYTER_DIR`,
  and `DATA_DIRECTORY` values.
- The existing on-start script.
- Standard Jupyter and SSH ports.

Append the following entry to the existing `PORTAL_CONFIG` value. Do not create
a second variable and do not remove or replace any existing application entry:

```text
|localhost:8188:8188:/:ComfyUI
```

Do not replace the on-start script. The ComfyUI portal entry is independent of
the Jupyter and SSH entries.

Keep the external and internal ports equal. A different internal port makes
Vast.ai start a Caddy reverse proxy on `8188`, which prevents ComfyUI from
binding to its default port.

## Profile settings

- Name: `ComfyUI Image Production`.
- Visibility: `Private`.
- Disk: model data from the selected `configs/profiles/*.json` file plus at
  least 40 GB.
- GPU: select according to the reduced workflow's requirements.
- Port: expose `8188/tcp` so the ComfyUI application card can reach the service.

An SSH tunnel remains available as a fallback:

```bash
ssh -p SSH_PORT root@HOST -L 8188:localhost:8188
```

Then open `http://127.0.0.1:8188` locally.

## Three new template variables

```text
PROVISIONING_SCRIPT=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/providers/vastai/provision.sh
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/qwen-image.json
```

Copy the template for another image family and change only its name, disk size,
GPU filters, and `CONFIG_URL` profile filename. Keep the ComfyUI portal entry
and exposed port unchanged.

Do not add `COMFY_VERSION` or `COMFY_PORT`. The version comes from
`comfyuiVersion` in the JSON profile, and the default port is `8188`.

With the five standard variables from the official PyTorch template, the final
set fits the 10-variable limit:

```text
5 standard + PROVISIONING_SCRIPT + REPO_RAW_BASE + CONFIG_URL
+ HF_TOKEN + CIVITAI_TOKEN = 10
```

## Vast.ai account secrets

Create two encrypted variables under `Account → Environment Variables`:

```text
HF_TOKEN=hf_...
CIVITAI_TOKEN=...
```

Never place token values in the template, GitHub, or JSON. Account-level
variables are automatically available to created instances. Omit a secret when
the selected profiles do not require that provider.

## Validation

Jupyter should open exactly as it does in the original official template.
The ComfyUI application card is present immediately on a newly created
instance, but it becomes usable only after provisioning starts ComfyUI on port
`8188`.

Follow provisioning with:

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
```

After provisioning completes:

```bash
bash /workspace/comfyui-cloud/runtime/check-install.sh
```
