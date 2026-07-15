#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"

if command -v supervisorctl >/dev/null 2>&1 && \
   supervisorctl status comfyui >/dev/null 2>&1; then
  PORT="${COMFY_PORT:-18188}"
  echo "ComfyUI service:"
  supervisorctl status comfyui
else
  PORT="${COMFY_PORT:-8188}"
  echo "ComfyUI process:"
  pgrep -af "python.*main.py" || true
fi

test -f "${COMFY_DIR}/main.py"
test -f "${STATE_DIR}/install-state.json"

if [[ -f "${STATE_DIR}/INSTALL_COMPLETE" ]]; then
  echo "All configured models are installed."
else
  echo "Model downloads are still running or require attention."
fi

if [[ -f "${STATE_DIR}/models.pid" ]]; then
  read -r models_pid < "${STATE_DIR}/models.pid" || true
  if [[ "${models_pid:-}" =~ ^[0-9]+$ ]] && kill -0 "${models_pid}" 2>/dev/null; then
    echo "Model downloader PID ${models_pid} is active."
  fi
fi

echo "Disk usage:"
du -sh "${COMFY_DIR}" "${WORKSPACE}/.cache" 2>/dev/null || true

curl --noproxy '*' -fsS --max-time 5 \
  "http://127.0.0.1:${PORT}/system_stats" >/dev/null
echo "ComfyUI responds on 127.0.0.1:${PORT}."
