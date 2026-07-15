#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
STATE_DIR="${WORKSPACE}/comfyui-cloud"
LOG_DIR="${STATE_DIR}/logs"
: "${REPO_RAW_BASE:?Set REPO_RAW_BASE to the raw GitHub repository URL}"
mkdir -p "${STATE_DIR}/runtime" "${LOG_DIR}"
printf '%s\n' '::' > "${STATE_DIR}/comfy-listen-host"
exec > >(tee -a "${LOG_DIR}/provision.log") 2>&1
export DEBIAN_FRONTEND=noninteractive STATE_DIR
apt-get update
apt-get install -y --no-install-recommends aria2 ca-certificates curl ffmpeg git jq libgl1 libglib2.0-0
rm -rf /var/lib/apt/lists/*
for file in install_from_config.py install.sh start-comfyui.sh check-install.sh; do
  curl -fL --retry 5 "${REPO_RAW_BASE}/common/${file}" -o "${STATE_DIR}/runtime/${file}"
done
chmod +x "${STATE_DIR}/runtime/"*.sh
export INSTALLER_PATH="${STATE_DIR}/runtime/install_from_config.py"
"${STATE_DIR}/runtime/install.sh"
"${STATE_DIR}/runtime/start-comfyui.sh"
