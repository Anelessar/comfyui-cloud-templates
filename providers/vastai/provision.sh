#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${WORKSPACE}/ComfyUI"
STATE_DIR="${WORKSPACE}/comfyui-cloud"
RUNTIME_DIR="${STATE_DIR}/runtime"
LOG_DIR="${STATE_DIR}/logs"
CONFIG_PATH="${STATE_DIR}/config.json"
EXPECTED_COMFY_VERSION="${VAST_COMFY_VERSION:-v0.27.0}"

: "${REPO_RAW_BASE:?Set REPO_RAW_BASE to the raw GitHub repository URL}"
: "${CONFIG_URL:?Set CONFIG_URL to a ComfyUI profile JSON URL}"

mkdir -p "${RUNTIME_DIR}" "${LOG_DIR}" "${WORKSPACE}/.cache/huggingface"
exec > >(tee -a "${LOG_DIR}/provision.log") 2>&1

echo "Vast.ai ComfyUI profile provisioning started at $(date -Is)"

if [[ -f /venv/main/bin/activate ]]; then
  # shellcheck disable=SC1091
  source /venv/main/bin/activate
fi

missing_packages=()
command -v aria2c >/dev/null 2>&1 || missing_packages+=(aria2)
command -v ffmpeg >/dev/null 2>&1 || missing_packages+=(ffmpeg)
if ((${#missing_packages[@]})); then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends "${missing_packages[@]}"
  rm -rf /var/lib/apt/lists/*
fi

curl -fL --retry 10 --retry-delay 5 \
  "${CONFIG_URL}" \
  -o "${CONFIG_PATH}"
curl -fL --retry 10 --retry-delay 5 \
  "${REPO_RAW_BASE}/common/install_from_config.py" \
  -o "${RUNTIME_DIR}/install_from_config.py"
curl -fL --retry 10 --retry-delay 5 \
  "${REPO_RAW_BASE}/common/check-install.sh" \
  -o "${RUNTIME_DIR}/check-install.sh"
chmod +x "${RUNTIME_DIR}/install_from_config.py" "${RUNTIME_DIR}/check-install.sh"

if [[ ! -f "${COMFY_DIR}/main.py" ]]; then
  echo "The official vastai/comfy image did not initialize ${COMFY_DIR}." >&2
  exit 1
fi

profile_version="$(python - "${CONFIG_PATH}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    print(json.load(handle)["comfyuiVersion"])
PY
)"
if [[ "${profile_version}" != "${EXPECTED_COMFY_VERSION}" ]]; then
  echo "Profile requires ComfyUI ${profile_version}, but the Vast template image provides ${EXPECTED_COMFY_VERSION}." >&2
  echo "Update the vastai/comfy image tag and VAST_COMFY_VERSION together." >&2
  exit 1
fi

export \
  HF_HOME="${WORKSPACE}/.cache/huggingface" \
  PIP_CACHE_DIR="${WORKSPACE}/.cache/pip" \
  PYTHONUNBUFFERED=1 \
  STATE_DIR \
  WORKSPACE

python "${RUNTIME_DIR}/install_from_config.py" \
  --config "${CONFIG_PATH}" \
  --comfy-dir "${COMFY_DIR}" \
  --validate-only

# The official image keeps its Supervisor-managed ComfyUI service paused while
# /.provisioning exists. Install nodes synchronously so the first ComfyUI start
# sees the complete node set, then let the large model downloads continue in
# the background after the official service is released.
python "${RUNTIME_DIR}/install_from_config.py" \
  --config "${CONFIG_PATH}" \
  --comfy-dir "${COMFY_DIR}" \
  --phase nodes

nohup python "${RUNTIME_DIR}/install_from_config.py" \
  --config "${CONFIG_PATH}" \
  --comfy-dir "${COMFY_DIR}" \
  --phase models \
  >> "${LOG_DIR}/models.log" 2>&1 &
models_pid=$!
echo "${models_pid}" > "${STATE_DIR}/models.pid"

echo "Custom nodes are ready. The official ComfyUI service can now start on internal port 18188."
echo "Model downloads continue in the background as PID ${models_pid}."
echo "Model log: ${LOG_DIR}/models.log"
echo "Vast.ai ComfyUI profile provisioning completed at $(date -Is)"
