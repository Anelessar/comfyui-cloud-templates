# Workflow profiles

These profiles were derived from the two original AI Launcher exports. Each
profile contains one usable model family or one post-processing workflow instead
of every unrelated model and custom node.

## Profile catalog

| Profile | Purpose | Model data |
| --- | --- | ---: |
| `qwen-image-edit-2511` | Qwen image editing with the four-step Lightning LoRA | 47.8 GiB |
| `qwen-image-edit-2511-multi-angle` | Qwen multi-angle product views | 47.3 GiB |
| `flux-uso` | FLUX.1 Dev identity customization with USO | 23.4 GiB |
| `z-image-turbo` | Z-Image Turbo text-to-image | 19.3 GiB |
| `krea-2-turbo` | Krea 2 Turbo text-to-image | 24.5 GiB |
| `image-detailer-upscale` | Face detection and image upscaling | 0.1 GiB |
| `wan22-animate` | Wan 2.2 character animation and replacement | 48.5 GiB |
| `wan22-t2v-14b-fp16` | Complete Wan 2.2 14B T2V expert pair | 64.1 GiB |
| `wan21-fun-control-14b` | Wan 2.1 Fun Control through WanVideoWrapper | 27.5 GiB |
| `video-rife-upscale` | RIFE interpolation and frame upscaling | 0.1 GiB |

The sizes cover model files only. Add at least 40 GiB for the container,
ComfyUI, Python packages, caches, inputs, and outputs.

## Intentional corrections

- Qwen diffusion weights and text encoders use their native ComfyUI model
  directories instead of the original `checkpoints` and `clip` paths.
- Wan 2.2 14B profiles use `wan_2.1_vae.safetensors`; `wan2.2_vae` is for the
  5B hybrid model.
- Wan 2.2 T2V includes both high-noise and low-noise experts. The original
  export contained only the low-noise expert and could not run a complete 14B
  T2V workflow.
- Wan Fun Control is stored under `diffusion_models`, not `loras`.
- The YOLO face detector is stored under `ultralytics/bbox` and includes Impact
  Subpack, which provides the current Ultralytics detector node.
- RIFE is stored inside the Frame Interpolation node's checkpoint directory and
  that node is installed before the model download starts.
- Only one copy of the duplicate Wan Animate relight LoRA is retained.

## Deliberately excluded items

The original exports also contain individual Wan I2V/T2V acceleration LoRAs.
Those adapters are not complete models and cannot form a working profile without
the matching high-noise and low-noise base models and a compatible sampling
graph. They were not published as misleading standalone profiles.

Generic nodes such as MultiGPU, Memory Cleanup, GGUF loaders, Florence2,
AdvancedLivePortrait, Swwan, TensorOps, ComfyMath, CRT Nodes, rgthree, and Custom
Scripts were not added everywhere. Add one only when an actual workflow JSON
contains one of its node types.

ComfyUI Manager and ComfyUI Hugging Face Downloader are intentionally included
in every profile as workflow-discovery tools. Remove them from a production-only
profile if startup speed and dependency isolation matter more than interactive
workflow inspection.

## Provider selection

Vast.ai uses the direct raw URL:

```text
CONFIG_URL=https://raw.githubusercontent.com/Anelessar/comfyui-cloud-templates/main/configs/profiles/qwen-image-edit-2511.json
```

RunPod accepts the profile filename without `.json`:

```text
PROFILE=qwen-image-edit-2511
```

The same RunPod image works for every profile.
