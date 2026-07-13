#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
PROFILE="${PROFILE:-}"
mkdir -p "${STATE_DIR}/logs"
if [[ -x /start.sh && "$(readlink -f /start.sh)" != "$(readlink -f "$0")" ]]; then /start.sh > "${STATE_DIR}/logs/runpod-base.log" 2>&1 & fi
if [[ -z "${CONFIG_URL:-}" ]]; then
  : "${REPO_RAW_BASE:?Set REPO_RAW_BASE or CONFIG_URL}"
  case "${PROFILE}" in
    image) CONFIG_URL="${REPO_RAW_BASE}/configs/image.json" ;;
    video) CONFIG_URL="${REPO_RAW_BASE}/configs/video.json" ;;
    *) echo "PROFILE must be image or video when CONFIG_URL is not set." >&2; exit 1 ;;
  esac
fi
export CONFIG_URL STATE_DIR INSTALLER_PATH=/opt/comfyui-cloud/common/install_from_config.py
/opt/comfyui-cloud/common/install.sh
cd "${COMFY_DIR:-/workspace/ComfyUI}"
read -r -a EXTRA_ARGS <<< "${COMFY_EXTRA_ARGS:-}"
exec python main.py --listen 0.0.0.0 --port "${COMFY_PORT:-8188}" --disable-auto-launch "${EXTRA_ARGS[@]}"
