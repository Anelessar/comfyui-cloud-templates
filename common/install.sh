#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
CONFIG_PATH="${CONFIG_PATH:-${STATE_DIR}/config.json}"
INSTALLER_PATH="${INSTALLER_PATH:-/opt/comfyui-cloud/common/install_from_config.py}"
INSTALL_PHASE="${INSTALL_PHASE:-all}"

: "${CONFIG_URL:?CONFIG_URL must point to a ComfyUI profile JSON file}"

mkdir -p \
  "${STATE_DIR}/logs" \
  "${WORKSPACE}/.cache/pip" \
  "${WORKSPACE}/.cache/huggingface"

export \
  STATE_DIR \
  PIP_CACHE_DIR="${WORKSPACE}/.cache/pip" \
  HF_HOME="${WORKSPACE}/.cache/huggingface" \
  PYTHONUNBUFFERED=1

if [[ -f /venv/main/bin/activate ]]; then
  # shellcheck disable=SC1091
  source /venv/main/bin/activate
fi

curl -fL --retry 10 --retry-delay 5 "${CONFIG_URL}" -o "${CONFIG_PATH}"

# The profile is the single source of truth. COMFY_VERSION remains an optional
# emergency override, but normally changing CONFIG_URL is all that is needed.
if [[ -z "${COMFY_VERSION:-}" ]]; then
  COMFY_VERSION="$(python - "${CONFIG_PATH}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    print(json.load(handle)["comfyuiVersion"])
PY
)"
fi

if [[ ! "${COMFY_VERSION}" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]*$ ]] || \
   [[ "${COMFY_VERSION}" == *..* ]]; then
  echo "Unsafe ComfyUI Git ref: ${COMFY_VERSION}" >&2
  exit 1
fi

python "${INSTALLER_PATH}" \
  --config "${CONFIG_PATH}" \
  --comfy-dir "${COMFY_DIR}" \
  --validate-only

python -m pip install --upgrade pip

if [[ ! -d "${COMFY_DIR}/.git" ]]; then
  mkdir -p "${COMFY_DIR}"
  git -C "${COMFY_DIR}" init
  git -C "${COMFY_DIR}" remote add origin https://github.com/Comfy-Org/ComfyUI.git
fi

git -C "${COMFY_DIR}" fetch --depth 1 origin "${COMFY_VERSION}"
git -C "${COMFY_DIR}" checkout --force --detach FETCH_HEAD

python -m pip install -r "${COMFY_DIR}/requirements.txt"
python "${INSTALLER_PATH}" \
  --config "${CONFIG_PATH}" \
  --comfy-dir "${COMFY_DIR}" \
  --phase "${INSTALL_PHASE}"

echo "Installation phase ${INSTALL_PHASE} completed for ${CONFIG_URL}"
