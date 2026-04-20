##########
########## BUILDER STAGE ##########
##########
FROM python:3.13-slim-bookworm AS builder

# install packages for safe build & clear unnecessary extra files
RUN apt-get update && apt-get install --no-install-recommends -y\
        build-essential \
        gcc \
        libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip wheel psycopg2

# install/copy uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# setup env path for uv commands to work
ENV PATH="/root/.local/bin:$PATH"

# set working directory
WORKDIR /builder_app
# copy requirements.txt for installation of dependencies
COPY pyproject.toml .
COPY uv.lock .
# install dependencies
RUN uv sync --locked
##########
########## END OF BUILDER STAGE ##########
##########


##########
########## FINAL STAGE ##########
##########
FROM python:3.13-slim-bookworm AS final

# install packages for safe build & clear unnecessary extra files
RUN apt-get update && apt-get install --no-install-recommends -y\
    libpq-dev \
    # && apt-get purge -y --auto-remove libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /backend_app

COPY ./src/ /backend_app/src/
COPY ./.migrations/ /backend_app/.migrations/
COPY ./create_superuser/ /backend_app/create_superuser/
COPY ./alembic.ini /backend_app/alembic.ini

COPY --from=builder /builder_app/.venv /backend_app/.venv

ENV PATH="/backend_app/.venv/bin:$PATH"
##########
########## END OF FINAL STAGE ##########
##########