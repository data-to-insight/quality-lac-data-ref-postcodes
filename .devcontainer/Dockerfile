FROM python:3.8-bullseye

# System deps for building old numpy/pandas from sdist if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    pkg-config \
    git \
    git-lfs \
    curl \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Keep pip/build tooling conservative (old numpy/pandas often break with very new setuptools/Cython)
RUN python -m pip install --upgrade "pip<24" \
  && python -m pip install \
       "setuptools<60" \
       "wheel<0.39" \
       "Cython<3" \
       "virtualenv<21.0.0"

# Install Poetry (pin it if you want full reproducibility)
ENV POETRY_VERSION=1.8.5
RUN curl -sSL https://install.python-poetry.org | python - --version ${POETRY_VERSION} \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Poetry config: keep the venv inside the repo for transparency
RUN poetry config virtualenvs.in-project true

WORKDIR /work

