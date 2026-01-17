# ---- Base image ----
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PROJECT_NAME=fitnesstracker
ENV VENV_PATH=/opt/venv

# ---- System dependencies ----
RUN echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      curl git unzip xz-utils \
      libgl1-mesa-dri libgtk-3-0 \
      python3 python3-venv python3-dev build-essential \
      ca-certificates \
      && rm -rf /var/lib/apt/lists/*

# ---- Create Python virtual environment ----
RUN python3 -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# ---- Install Python packages inside venv ----
RUN pip install --no-cache-dir --upgrade pip requests

# ---- Install Flutter SDK ----
RUN git clone https://github.com/flutter/flutter.git /opt/flutter -b stable
ENV PATH="/opt/flutter/bin:/opt/flutter/bin/cache/dart-sdk/bin:$PATH"

# ---- Flutter setup ----
RUN flutter doctor
RUN flutter config --enable-web
RUN flutter precache --web

# ---- Working directory ----
WORKDIR /app

# ---- Copy entrypoint ----
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
