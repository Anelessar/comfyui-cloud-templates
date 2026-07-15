#!/usr/bin/env bash
set -Eeuo pipefail
WORKSPACE="${WORKSPACE:-/workspace}"
COMFY_DIR="${COMFY_DIR:-${WORKSPACE}/ComfyUI}"
STATE_DIR="${STATE_DIR:-${WORKSPACE}/comfyui-cloud}"
LOG_DIR="${STATE_DIR}/logs"
PORT="${COMFY_PORT:-8188}"
mkdir -p "${LOG_DIR}"
if [[ -f /venv/main/bin/activate ]]; then source /venv/main/bin/activate; fi
if [[ ! -f "${COMFY_DIR}/main.py" ]]; then echo "ComfyUI is not installed at ${COMFY_DIR}" >&2; exit 1; fi
if pgrep -f "python.*${COMFY_DIR}/main.py.*--port ${PORT}" >/dev/null 2>&1; then echo "ComfyUI is already running on port ${PORT}."; exit 0; fi
cd "${COMFY_DIR}"
read -r -a EXTRA_ARGS <<< "${COMFY_EXTRA_ARGS:-}"
nohup python "${COMFY_DIR}/main.py" --listen 0.0.0.0 --port "${PORT}" --disable-auto-launch "${EXTRA_ARGS[@]}" >> "${LOG_DIR}/comfyui.log" 2>&1 &
PID=$!
echo "${PID}" > "${STATE_DIR}/comfyui.pid"

for _ in {1..60}; do
  if ! kill -0 "${PID}" 2>/dev/null; then
    echo "ComfyUI exited before port ${PORT} became ready." >&2
    tail -n 80 "${LOG_DIR}/comfyui.log" >&2 || true
    exit 1
  fi

  if python - "${PORT}" <<'PY'
import sys
import urllib.request

with urllib.request.urlopen(
    f"http://127.0.0.1:{int(sys.argv[1])}/system_stats",
    timeout=1,
) as response:
    if response.status != 200:
        raise RuntimeError(f"Unexpected HTTP status: {response.status}")
PY
  then
    echo "ComfyUI is ready on port ${PORT}."
    exit 0
  fi

  sleep 1
done

echo "ComfyUI did not become ready on port ${PORT} within 60 seconds." >&2
tail -n 80 "${LOG_DIR}/comfyui.log" >&2 || true
exit 1
