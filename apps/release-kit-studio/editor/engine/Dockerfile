FROM python:3.12-slim-bookworm@sha256:54c85f3c47607a77f32adec749d3c81d1348bf25833671f512b26a9b6d778cb3
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fontconfig fonts-noto-core && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --uid 10001 editor
WORKDIR /app
COPY engine.py server.py visual_diagnostics.py preview.py /app/
USER editor
ENV EDITOR_SCRATCH=/tmp/release-kit-editor
EXPOSE 8080
CMD ["python3", "/app/server.py"]
