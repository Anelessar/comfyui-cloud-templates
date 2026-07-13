#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
CONFIG_PATH="${CONFIG_PATH:-${STATE_DIR}/config.json}"
COMFY_VERSION="${COMFY_VERSION:-v0.27.0}"
INSTALLER_PATH="${INSTALLER_PATH:-/opt/comfyui-cloud/common/install_from_config.py}"
: "${CONFIG_URL:?CONFIG_URL must point to configs/image.json or configs/video.json}"
mkdir -p "${STATE_DIR}/logs" "${WORKSPACE}/.cache/pip" "${WORKSPACE}/.cache/huggingface"
export STATE_DIR PIP_CACHE_DIR="${WORKSPACE}/.cache/pip" HF_HOME="${WORKSPACE}/.cache/huggingface" PYTHONUNBUFFERED=1
if [[ -f /venv/main/bin/activate ]]; then source /venv/main/bin/activate; fi
curl -fL --retry 10 --retry-delay 5 "${CONFIG_URL}" -o "${CONFIG_PATH}"
python -m pip install --upgrade pip setuptools wheel
if [[ ! -d "${COMFY_DIR}/.git" ]]; then
  git clone --depth 1 --branch "${COMFY_VERSION}" https://github.com/Comfy-Org/ComfyUI.git "${COMFY_DIR}"
else
  git -C "${COMFY_DIR}" fetch --tags --force
  git -C "${COMFY_DIR}" checkout --force "${COMFY_VERSION}"
fi
python -m pip install -r "${COMFY_DIR}/requirements.txt"
python "${INSTALLER_PATH}" --config "${CONFIG_PATH}" --comfy-dir "${COMFY_DIR}"
echo "Installation completed for ${CONFIG_URL}"
