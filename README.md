# ComfyUI Cloud Templates

A shared installer for Vast.ai and RunPod. Each model and custom-node set is
defined by a JSON profile in `configs/`.

## Fixes included

- Vast.ai no longer requires changes to `PORTAL_CONFIG` or the on-start script.
- A failed optional `pip install -e` for one node no longer stops provisioning.
- `comfyuiVersion` is read from the selected JSON profile.
- Private and gated Hugging Face and Civitai models are supported.
- `HF_TOKEN` and `CIVITAI_TOKEN` are redacted from commands and errors.
- Interrupted model downloads resume through `aria2c`.
- Existing models use a stricter completeness check.
- Custom nodes can be pinned with a `commit` field.

## Adding a workflow

Ten reduced profiles are available under `configs/profiles/`. See the profile
catalog in `configs/profiles/README.md` for their purpose and model size.

Create another profile with the included builder instead of copying model
objects by hand:

```bash
python3 tools/profile_builder.py list configs/image.json
python3 tools/profile_builder.py create \
  configs/image.json \
  configs/profiles/product-photo.json \
  --name product-photo \
  --models 1,2,3,4 \
  --nodes 10 \
  --with-discovery-tools
```

Keep only the models and nodes required by that workflow. See
`configs/README.md` for the complete schema and private-model examples.

Then point `CONFIG_URL` to the new profile:

```text
https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/product-photo.json
```

Provider scripts do not need to change.

The top-level `image.json` and `video.json` files remain unchanged as source
exports and are still large. They are not the recommended profiles for fresh,
disposable GPUs. Tokens do not make large transfers substantially smaller;
selecting one reduced workflow profile is the effective startup optimization.

## Vast.ai

Use:

- `providers/vastai/image-template.md`
- `providers/vastai/video-template.md`

Copy a working official PyTorch template. Do not change its `PORTAL_CONFIG`,
on-start script, Jupyter configuration, or SSH configuration. Add only the three
repository/profile URL variables. Store tokens separately as account-level
environment variables.

## RunPod

GitHub Actions builds the shared image:

```text
ghcr.io/anelessar/comfyui-cloud:latest
```

Use:

- `providers/runpod/image-template.md`
- `providers/runpod/video-template.md`

For disposable Pods without persistent storage, set the volume size to `0 GB`
and size the container disk to the profile's model data plus 40–50 GB.

Set `PROFILE` to any filename under `configs/profiles/` without `.json`, for
example `PROFILE=z-image-turbo`. A direct `CONFIG_URL` remains supported.

## Logs and validation

Vast.ai:

```bash
tail -f /workspace/comfyui-cloud/logs/provision.log
bash /workspace/comfyui-cloud/runtime/check-install.sh
```

RunPod:

```bash
bash /opt/comfyui-cloud/common/check-install.sh
```

ComfyUI log:

```bash
tail -f /workspace/comfyui-cloud/logs/comfyui.log
```

## Secrets

Never commit real secret values to GitHub, JSON profiles, or plain-text
templates. The supported variable names are:

```text
HF_TOKEN
CIVITAI_TOKEN
```

For a gated Hugging Face model, the account owning `HF_TOKEN` must also receive
access to the repository or accept its license.
