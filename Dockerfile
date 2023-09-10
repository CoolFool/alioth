FROM python:3.11.5-slim-bookworm as base

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN mkdir /app

FROM base as python-base

RUN apt-get update \
  && apt-get -y upgrade\
  && apt-get install --no-install-recommends -y \
  curl  \
  && rm -rf /var/lib/apt/lists/*  \
  && rm -rf /tmp/*

ENV POETRY_VERSION=1.4.2
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org/ | python
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev

FROM base as final

RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  make \
  && apt-get clean \
  && apt-get autoremove \
  && rm -rf /var/lib/apt/lists/*  \
  && rm -rf /tmp/*

WORKDIR /app
ENV PYTHONPATH="${PYTHONPATH}:/app"

COPY --from=python-base $VENV_PATH $VENV_PATH
COPY . ./

EXPOSE 1337