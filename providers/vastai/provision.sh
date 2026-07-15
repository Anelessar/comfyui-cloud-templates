#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
STATE_DIR="${WORKSPACE}/comfyui-cloud"
LOG_DIR="${STATE_DIR}/logs"
: "${REPO_RAW_BASE:?Set REPO_RAW_BASE to the raw GitHub repository URL}"
mkdir -p "${STATE_DIR}/runtime" "${LOG_DIR}"
printf '%s\n' '0.0.0.0' > "${STATE_DIR}/comfy-listen-host"
exec > >(tee -a "${LOG_DIR}/provision.log") 2>&1

# The Vast application tunnel is created before provisioning finishes. Serve a
# small auto-refreshing status page immediately so the application shows useful
# progress instead of Cloudflare 502 while dependencies are installed.
STATUS_DIR="${STATE_DIR}/status-page"
STATUS_PID_FILE="${STATE_DIR}/status-server.pid"
mkdir -p "${STATUS_DIR}"
printf '%s\n' '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="5"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ComfyUI is installing</title><style>body{font-family:system-ui,sans-serif;max-width:720px;margin:15vh auto;padding:32px;background:#111;color:#eee}h1{font-size:2rem}p{line-height:1.6;color:#bbb}</style></head><body><h1>ComfyUI is installing</h1><p>The interface will open automatically when ComfyUI and its custom nodes are ready. Model downloads will continue after the interface becomes available.</p></body></html>' > "${STATUS_DIR}/index.html"
if [[ ! -f "${STATUS_PID_FILE}" ]] || ! kill -0 "$(cat "${STATUS_PID_FILE}" 2>/dev/null || true)" 2>/dev/null; then
  nohup python -m http.server 8188 --bind '0.0.0.0' --directory "${STATUS_DIR}" >> "${LOG_DIR}/status-server.log" 2>&1 &
  echo "$!" > "${STATUS_PID_FILE}"
fi

export DEBIAN_FRONTEND=noninteractive STATE_DIR
apt-get update
apt-get install -y --no-install-recommends aria2 ca-certificates curl ffmpeg git jq libgl1 libglib2.0-0
rm -rf /var/lib/apt/lists/*
for file in install_from_config.py install.sh start-comfyui.sh check-install.sh; do
  curl -fL --retry 5 "${REPO_RAW_BASE}/common/${file}" -o "${STATE_DIR}/runtime/${file}"
done
chmod +x "${STATE_DIR}/runtime/"*.sh
export INSTALLER_PATH="${STATE_DIR}/runtime/install_from_config.py"
export INSTALL_PHASE=nodes
"${STATE_DIR}/runtime/install.sh"
"${STATE_DIR}/runtime/start-comfyui.sh"

# Keep the UI available while large model files download. The portal tunnel is
# created at container startup, so starting ComfyUI before this phase prevents
# a long-lived 502 page during initial provisioning.
python "${INSTALLER_PATH}" \
  --config "${STATE_DIR}/config.json" \
  --comfy-dir "${WORKSPACE}/ComfyUI" \
  --phase models
