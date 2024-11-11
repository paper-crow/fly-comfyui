ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim

# Fail fast on errors or unset variables
SHELL ["/bin/bash", "-eux", "-o", "pipefail", "-c"]

ENV COMFYUI_ADDRESS=0.0.0.0
ENV COMFYUI_PORT=8188

WORKDIR /app

# Configure pip to use cache
ENV XDG_CACHE_HOME=/cache
ENV PIP_CACHE_DIR=/cache/pip

# create cache directory. During build we will use a cache mount,
# but later this is useful for custom node installs
RUN --mount=type=cache,target=/cache/ \
    mkdir -p ${PIP_CACHE_DIR}

# Install build dependencies and configure pip cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git \
      git-lfs \
      rsync \
      fonts-recommended \
      curl \
      build-essential \
      libssl-dev \
      libffi-dev \
      libgl1-mesa-glx \
      libglib2.0-0 \
      python3-dev \
      unzip \
      yq \
      jq

# Use buildkit cache mount for pip
RUN --mount=type=cache,target=/cache/pip \
    pip install --upgrade pip cmake

# Default System Requirements
COPY ./system_requirements.txt /cache/

RUN --mount=type=cache,target=/cache/pip \
    pip install -r /cache/system_requirements.txt

# Clone ComfyUI
RUN git clone --depth 1 --branch v0.2.3 https://github.com/comfyanonymous/ComfyUI.git .

RUN --mount=type=cache,target=/cache/pip \
    pip install -r requirements.txt

# Copy scripts and configuration
COPY ./entrypoint.sh ./download-custom-nodes.py ./download-models.py ./
RUN chmod +x entrypoint.sh

COPY ./workflows.yml ./

# Install custom nodes using the Python script
RUN --mount=type=cache,target=/cache/pip \
    python download-custom-nodes.py && \
    for dir in custom_nodes/*/; do \
        if [ -f "${dir}requirements.txt" ]; then \
            pip install -r "${dir}requirements.txt"; \
        fi \
    done

ENTRYPOINT [ "./entrypoint.sh" ]

# default start command
CMD python -u main.py \
  --listen ${COMFYUI_ADDRESS} \
  --port ${COMFYUI_PORT}
