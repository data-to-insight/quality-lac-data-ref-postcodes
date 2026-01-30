FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    git-lfs \
    curl \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install Node.js, npm, and pnpm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && npm install -g pnpm \
  && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install modern build tools
RUN python -m pip install --upgrade pip setuptools wheel

# Install Poetry (latest version)
RUN curl -sSL https://install.python-poetry.org | python - \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Poetry config: keep the venv inside the repo for transparency
RUN poetry config virtualenvs.in-project true

WORKDIR /work

