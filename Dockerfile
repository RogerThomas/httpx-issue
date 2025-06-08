FROM python:3.12.10-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /bin/uv
WORKDIR /app
COPY . /app
ENTRYPOINT ["uv", "run"]
CMD ["fastapi", "dev", "server.py", "--port", "8000", "--host", "0.0.0.0"]
