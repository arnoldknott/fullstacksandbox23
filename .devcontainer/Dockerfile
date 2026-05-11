# check=skip=InvalidDefaultArgInFrom
ARG PYTHON_VERSION
ARG NODE_VERSION
ARG ALPINE_VERSION
ARG UV_VERSION
ARG BUN_VERSION

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv-base

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS python-base

FROM node:${NODE_VERSION}-alpine${ALPINE_VERSION} AS node-base

FROM node-base AS base

ARG BUN_VERSION

COPY --from=python-base /usr/local /usr/local
COPY --from=uv-base /uv /uvx /bin/
RUN npm install -g bun@${BUN_VERSION}

RUN apk add --no-cache bash ca-certificates curl git openssh-client \
    && uv venv /opt/az \
    && apk add --no-cache --virtual=build gcc musl-dev python3-dev libffi-dev openssl-dev cargo make \
    && uv pip install --python /opt/az/bin/python --no-cache azure-cli \
    && apk del build \
    && ln -sf /opt/az/bin/az /usr/local/bin/az

WORKDIR /workspaces