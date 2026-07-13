#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
LOG_DIR="${STATE_DIR}/logs"
PORT="${COMFY_PORT:-8188}"
mkdir -p "${LOG_DIR}"
if [[ -f /venv/main/bin/activate ]]; then source /venv/main/bin/activate; fi
if [[ ! -f "${COMFY_DIR}/main.py" ]]; then echo "ComfyUI is not installed at ${COMFY_DIR}" >&2; exit 1; fi
if pgrep -f "python.*${COMFY_DIR}/main.py.*--port ${PORT}" >/dev/null 2>&1; then echo "ComfyUI is already running on port ${PORT}."; exit 0; fi
cd "${COMFY_DIR}"
read -r -a EXTRA_ARGS <<< "${COMFY_EXTRA_ARGS:-}"
nohup python "${COMFY_DIR}/main.py" --listen 0.0.0.0 --port "${PORT}" --disable-auto-launch "${EXTRA_ARGS[@]}" >> "${LOG_DIR}/comfyui.log" 2>&1 &
echo $! > "${STATE_DIR}/comfyui.pid"
echo "Started ComfyUI on port ${PORT}."
