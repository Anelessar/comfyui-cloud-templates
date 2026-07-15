#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
LOG_DIR="${STATE_DIR}/logs"
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
HEALTH_URL="http://${HEALTH_HOST}:${PORT}/system_stats"
mkdir -p "${LOG_DIR}"
if [[ -f /venv/main/bin/activate ]]; then source /venv/main/bin/activate; fi
if [[ ! -f "${COMFY_DIR}/main.py" ]]; then echo "ComfyUI is not installed at ${COMFY_DIR}" >&2; exit 1; fi
if pgrep -f "python.*${COMFY_DIR}/main.py.*--port ${PORT}" >/dev/null 2>&1; then echo "ComfyUI is already running on port ${PORT}."; exit 0; fi
cd "${COMFY_DIR}"
read -r -a EXTRA_ARGS <<< "${COMFY_EXTRA_ARGS:-}"
nohup python "${COMFY_DIR}/main.py" --listen "${LISTEN_HOST}" --port "${PORT}" --disable-auto-launch "${EXTRA_ARGS[@]}" >> "${LOG_DIR}/comfyui.log" 2>&1 &
PID=$!
echo "${PID}" > "${STATE_DIR}/comfyui.pid"

for _ in {1..60}; do
  if ! kill -0 "${PID}" 2>/dev/null; then
    echo "ComfyUI exited before port ${PORT} became ready." >&2
    tail -n 80 "${LOG_DIR}/comfyui.log" >&2 || true
    exit 1
  fi

  if curl --noproxy '*' -g -fsS --max-time 1 "${HEALTH_URL}" >/dev/null
  then
    echo "ComfyUI is ready on ${LISTEN_HOST}:${PORT}."
    exit 0
  fi

  sleep 1
done

echo "ComfyUI did not become ready on port ${PORT} within 60 seconds." >&2
tail -n 80 "${LOG_DIR}/comfyui.log" >&2 || true
exit 1
