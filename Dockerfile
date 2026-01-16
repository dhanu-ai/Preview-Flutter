FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PROJECT_NAME=fitnesstracker

# Network stability
RUN echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4

# System deps
RUN apt-get update -o Acquire::Retries=5 && \
    apt-get install -y --no-install-recommends \
      curl \
      git \
      unzip \
      xz-utils \
      libgl1-mesa-dri \
      libgtk-3-0 \
      python3 \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git /opt/flutter -b stable

ENV PATH="/opt/flutter/bin:/opt/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Flutter setup
RUN flutter doctor
RUN flutter config --enable-web
RUN flutter precache --web

WORKDIR /app

# Copy AI JSON
COPY _mXaP2CpM_XDOu8UhbrIk.json /app/project.json

# Build on container start
CMD ["bash", "-c", "\
set -e && \
echo '🚀 Creating Flutter project' && \
flutter create $PROJECT_NAME && \
cd $PROJECT_NAME && \
\
echo '🧠 Writing files from JSON' && \
python3 - << 'EOF'\n\
import json, os\n\
with open('/app/project.json') as f:\n\
    data = json.load(f)\n\
root = '/app/fitnesstracker'\n\
for path, content in data['files'].items():\n\
    full = os.path.join(root, path)\n\
    os.makedirs(os.path.dirname(full), exist_ok=True)\n\
    with open(full, 'w') as fp:\n\
        fp.write(content)\n\
print('✅ Files written')\n\
EOF\n\
\
echo '📦 flutter pub get' && \
flutter pub get && \
\
echo '🌐 Building Flutter Web' && \
flutter build web && \
\
echo '📤 Dumping build to /ui' && \
mkdir -p /ui && \
cp -r build/web/* /ui && \
\
echo '✅ Flutter Web build completed' \
"]
