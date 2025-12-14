FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
  curl git unzip xz-utils \
  libgl1-mesa-dri libgtk-3-0 \
  python3 \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git /opt/flutter -b stable
ENV PATH="/opt/flutter/bin:/opt/flutter/bin/cache/dart-sdk/bin:${PATH}"

RUN flutter config --enable-web
RUN flutter precache --web

WORKDIR /app

COPY server.py /server.py

EXPOSE 8080
EXPOSE 7000

CMD ["python3", "/server.py"]
