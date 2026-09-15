FROM python:3.11-slim

WORKDIR /app

# System deps some ML libraries need at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install -e ".[dev]" || true

COPY . .

CMD ["bash"]
