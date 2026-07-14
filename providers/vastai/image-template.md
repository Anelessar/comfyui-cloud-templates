# Vast.ai — Image template

Create this template by copying an official PyTorch template that already opens
Jupyter successfully on a selected machine.

## Keep unchanged

- The official PyTorch Docker image.
- Launch mode: `Jupyter + SSH`.
- Existing `PORTAL_CONFIG`, `OPEN_BUTTON_*`, `JUPYTER_DIR`, and
  `DATA_DIRECTORY` values.
- The existing on-start script.
- Standard Jupyter and SSH ports.

Do not add ComfyUI to `PORTAL_CONFIG` and do not replace the on-start script.
Those changes previously broke external access to a running Jupyter server.

## Profile settings

- Name: `ComfyUI Image Production`.
- Visibility: `Private`.
- Disk: model data from the selected `configs/profiles/*.json` file plus at
  least 40 GB.
- GPU: select according to the reduced workflow's requirements.
- Port: add `8188/tcp` only when direct external ComfyUI access is required.

Without a separate mapped port, use an SSH tunnel:

```bash
ssh -p SSH_PORT root@HOST -L 8188:localhost:8188
```

Then open `http://127.0.0.1:8188` locally.

## Three new template variables

```text
PROVISIONING_SCRIPT=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/providers/vastai/provision.sh
REPO_RAW_BASE=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/qwen-image-edit-2511.json
```

Copy the template for another image workflow and change only its name, disk
size, GPU filters, and `CONFIG_URL` profile filename.

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
Follow provisioning with:

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
```

After provisioning completes:

```bash
bash /workspace/comfyui-cloud/runtime/check-install.sh
```
