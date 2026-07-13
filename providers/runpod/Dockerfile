ARG RUNPOD_BASE_IMAGE=runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404
FROM ${RUNPOD_BASE_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 WORKSPACE=/workspace COMFY_DIR=/workspace/ComfyUI STATE_DIR=/workspace/comfyui-cloud COMFY_PORT=8188
RUN apt-get update && apt-get install -y --no-install-recommends aria2 ca-certificates curl ffmpeg git jq libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/comfyui-cloud
COPY common/ /opt/comfyui-cloud/common/
COPY providers/runpod/start.sh /opt/comfyui-cloud/start.sh
RUN chmod +x /opt/comfyui-cloud/start.sh /opt/comfyui-cloud/common/*.sh
EXPOSE 8188
CMD ["/opt/comfyui-cloud/start.sh"]
