#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
PORT="${COMFY_PORT:-8188}"
test -f "${COMFY_DIR}/main.py"
test -f "${STATE_DIR}/INSTALL_COMPLETE"
test -f "${STATE_DIR}/install-state.json"
echo "Disk usage:"; du -sh "${COMFY_DIR}" "${WORKSPACE}/.cache" 2>/dev/null || true
echo; echo "ComfyUI process:"; pgrep -af "python.*main.py" || true
echo
curl -fsS --max-time 5 "http://127.0.0.1:${PORT}/" >/dev/null && echo "ComfyUI responds on port ${PORT}."
