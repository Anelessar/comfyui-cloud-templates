#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
PORT="${COMFY_PORT:-8188}"
LISTEN_HOST="${COMFY_LISTEN:-}"
if [[ -z "${LISTEN_HOST}" && -f "${STATE_DIR}/comfy-listen-host" ]]; then
  read -r LISTEN_HOST < "${STATE_DIR}/comfy-listen-host"
fi
LISTEN_HOST="${LISTEN_HOST:-0.0.0.0}"
if [[ "${LISTEN_HOST}" == *:* ]]; then
  HEALTH_HOST="[::1]"
else
  HEALTH_HOST="127.0.0.1"
fi
test -f "${COMFY_DIR}/main.py"
test -f "${STATE_DIR}/INSTALL_COMPLETE"
test -f "${STATE_DIR}/install-state.json"
echo "Disk usage:"; du -sh "${COMFY_DIR}" "${WORKSPACE}/.cache" 2>/dev/null || true
echo; echo "ComfyUI process:"; pgrep -af "python.*main.py" || true
echo
curl --noproxy '*' -g -fsS --max-time 5 "http://${HEALTH_HOST}:${PORT}/" >/dev/null && \
  echo "ComfyUI responds on ${LISTEN_HOST}:${PORT}."
