# ComfyUI Cloud Templates

A shared installer for Vast.ai and RunPod. Each model and custom-node set is
defined by a JSON profile in `configs/`.

## Fixes included

- Vast.ai templates preserve the existing portal entries and append a ComfyUI
  application entry without changing the on-start script.
- A failed optional `pip install -e` for one node no longer stops provisioning.
- `comfyuiVersion` is read from the selected JSON profile.
- Private and gated Hugging Face and Civitai models are supported.
- `HF_TOKEN` and `CIVITAI_TOKEN` are redacted from commands and errors.
- Interrupted model downloads resume through `aria2c`.
- Existing models use a stricter completeness check.
- Custom nodes can be pinned with a `commit` field.

## Adding or extending a model family

Five model-family profiles are available under `configs/profiles/`. See the profile
catalog in `configs/profiles/README.md` for their purpose and model size.

Add another Qwen, Wan, FLUX, Z-Image, or Krea variant to the existing family
JSON. Create a new profile only when the model belongs to a different family.

For a new family, use the included builder instead of copying model objects by
hand:

```bash
python3 tools/profile_builder.py list configs/image.json
python3 tools/profile_builder.py create \
  configs/image.json \
  configs/profiles/new-image-family.json \
  --name new-image-family \
  --models 1,2,3,4 \
  --nodes 10 \
  --with-discovery-tools
```

Keep the shared base models, encoders, VAEs, adapters, and nodes used by that
family. See
`configs/README.md` for the complete schema and private-model examples.

Then point `CONFIG_URL` to the new profile:

```text
https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/new-image-family.json
```

Provider scripts do not need to change.

The top-level `image.json` and `video.json` files remain unchanged as source
exports and are still large. They are not the recommended profiles for fresh,
disposable GPUs. Tokens do not make large transfers substantially smaller;
selecting one reduced model-family profile is the effective startup
optimization.

## Vast.ai

Use:

- `providers/vastai/image-template.md`
- `providers/vastai/video-template.md`

Copy a working official PyTorch template. Keep its existing `PORTAL_CONFIG`
value and append the following entry to the same variable:

```text
|localhost:8188:18188:/:ComfyUI
```

Do not create a second `PORTAL_CONFIG` variable. Keep the on-start script,
Jupyter configuration, and SSH configuration unchanged, and expose container
port `8188`. Add only the three repository/profile URL variables. Store tokens
separately as account-level environment variables.

This change applies only to instances created from an updated template. An
already-created instance does not receive a new application card retroactively.

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
example `PROFILE=z-image`. A direct `CONFIG_URL` remains supported.

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
