# Model-family profiles

The two original AI Launcher exports are consolidated into five model-family
profiles. A family profile supports several related workflows and variants while
storing shared encoders, VAEs, utility models, and custom nodes only once.

## Profile catalog

| Profile | Included family | Model data |
| --- | --- | ---: |
| `qwen-image` | Qwen Image Edit, Lightning, multi-angle, face detailer, and upscale | 48.2 GiB |
| `flux` | FLUX.1 Dev and USO identity customization | 23.4 GiB |
| `z-image` | Z-Image Turbo and its shared encoder/VAE | 19.3 GiB |
| `krea-2` | Krea 2 Turbo | 24.5 GiB |
| `wan-video` | Wan Animate, T2V low-noise, Fun Control, LoRAs, RIFE, and upscale | 95.5 GiB |

The sizes cover model files only. Add at least 40 GiB for the container,
ComfyUI, Python packages, caches, inputs, and outputs. Video jobs may need more
temporary output space.

## Family decisions

### Qwen Image

One profile contains the Qwen Image Edit 2511 base, text encoder, VAE,
Lightning LoRA, multi-angle LoRA, the matching multi-angle node, and the small
detailer/upscale toolchain. A workflow can select the required Qwen variant
without creating another cloud template.

Future Qwen Image revisions and acceleration variants belong in this same
profile when they reuse the Qwen Image toolchain.

### Wan Video

One profile contains the Wan set from the original export: Animate, the
exported T2V low-noise model, Fun Control, both VAE variants, CLIP Vision, SAM,
acceleration and relight LoRAs, RIFE, and the upscaler. Wan-specific and
workflow-utility nodes are installed once.

The additional 27 GiB T2V high-noise expert is intentionally not injected into
this family profile because it was not present in the source export and would
increase the profile to approximately 122 GiB. Add it only when a particular
native dual-expert T2V graph actually requires it.

### Other image families

FLUX, Z-Image, and Krea 2 remain separate because they use different base
architectures and model files. Combining them would recreate the original
100+ GiB image profile without improving workflow compatibility.

## Custom-node policy

ComfyUI Manager and ComfyUI Hugging Face Downloader are included in every
family for workflow inspection. Family-specific nodes are installed only where
their models or graphs require them. GGUF loaders are omitted because these
profiles contain no GGUF weights. Florence2, AdvancedLivePortrait, and Custom
Scripts are omitted because they are optional workflow tools rather than
dependencies of one listed model family. Generic MultiGPU and Memory Cleanup
nodes are excluded because they are runtime choices rather than model-family
dependencies.

## Provider selection

Vast.ai uses the direct raw URL:

```text
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/qwen-image.json
```

RunPod accepts the profile filename without `.json`:

```text
PROFILE=qwen-image
```

The same RunPod image works for every family.
