#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
LOG_DIR="${STATE_DIR}/logs"
PORT="${COMFY_PORT:-8188}"
START_TIMEOUT="${COMFY_START_TIMEOUT:-300}"
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
STATUS_PID_FILE="${STATE_DIR}/status-server.pid"
if [[ ! "${START_TIMEOUT}" =~ ^[1-9][0-9]*$ ]]; then
  echo "COMFY_START_TIMEOUT must be a positive integer." >&2
  exit 1
fi
mkdir -p "${LOG_DIR}"
if [[ -f /venv/main/bin/activate ]]; then source /venv/main/bin/activate; fi
if [[ ! -f "${COMFY_DIR}/main.py" ]]; then echo "ComfyUI is not installed at ${COMFY_DIR}" >&2; exit 1; fi

# Vast provisioning exposes a temporary installation page on the final port so
# the application tunnel never has to show a long-lived 502. Stop only that
# tracked helper process immediately before ComfyUI takes over the port.
if [[ -f "${STATUS_PID_FILE}" ]]; then
  read -r STATUS_PID < "${STATUS_PID_FILE}" || true
  if [[ "${STATUS_PID:-}" =~ ^[0-9]+$ ]] && kill -0 "${STATUS_PID}" 2>/dev/null; then
    kill "${STATUS_PID}" 2>/dev/null || true
    for _ in {1..20}; do
      kill -0 "${STATUS_PID}" 2>/dev/null || break
      sleep 0.25
    done
  fi
  rm -f "${STATUS_PID_FILE}"
fi

PID="$(pgrep -f "python.*${COMFY_DIR}/main.py.*--port ${PORT}" | head -n 1 || true)"
if [[ -n "${PID}" ]]; then
  echo "ComfyUI process ${PID} is already starting or running on port ${PORT}."
else
  cd "${COMFY_DIR}"
  read -r -a EXTRA_ARGS <<< "${COMFY_EXTRA_ARGS:-}"
  nohup python "${COMFY_DIR}/main.py" --listen "${LISTEN_HOST}" --port "${PORT}" --disable-auto-launch "${EXTRA_ARGS[@]}" >> "${LOG_DIR}/comfyui.log" 2>&1 &
  PID=$!
  echo "${PID}" > "${STATE_DIR}/comfyui.pid"
fi

for ((elapsed = 0; elapsed < START_TIMEOUT; elapsed++)); do
  if ! kill -0 "${PID}" 2>/dev/null; then
    echo "ComfyUI exited before port ${PORT} became ready." >&2
    tail -n 80 "${LOG_DIR}/comfyui.log" >&2 || true
    exit 1
  fi

  if curl --noproxy '*' -g -fsS --max-time 1 "${HEALTH_URL}" >/dev/null
  then
    printf '%s\n' 'ok' > "${STATE_DIR}/COMFY_READY"
    echo "ComfyUI is ready on ${LISTEN_HOST}:${PORT}."
    exit 0
  fi

  sleep 1
done

echo "ComfyUI did not become ready on port ${PORT} within ${START_TIMEOUT} seconds." >&2
tail -n 80 "${LOG_DIR}/comfyui.log" >&2 || true
exit 1
