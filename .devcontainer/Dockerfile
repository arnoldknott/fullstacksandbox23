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
ARG OPENTOFU_VERSION

COPY --from=python-base /usr/local /usr/local
COPY --from=uv-base /uv /uvx /bin/
RUN npm install -g bun@${BUN_VERSION}

RUN apk add --no-cache bash ca-certificates curl docker-cli docker-cli-buildx docker-cli-compose git openssh-client \
    && uv venv /opt/az \
    && apk add --no-cache --virtual=build gcc musl-dev python3-dev libffi-dev openssl-dev cargo make \
    && uv pip install --python /opt/az/bin/python --no-cache --prerelease=allow azure-cli \
    && sed -i 's|^python -m azure.cli|/opt/az/bin/python -m azure.cli|' /opt/az/bin/az \
    && apk del build \
    && ln -sf /opt/az/bin/az /usr/local/bin/az

# Install the OpenTofu CLI (standalone) so the OpenTofu VS Code language server can
# extract provider schemas for IntelliSense and validation. tofu-ls ships no bundled
# schemas and runs the `tofu` binary itself. Mirrors infrastructure/Dockerfile.
RUN apk add --no-cache gnupg \
    && curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o /tmp/install-opentofu.sh \
    && chmod +x /tmp/install-opentofu.sh \
    && /tmp/install-opentofu.sh --install-method standalone --opentofu-version ${OPENTOFU_VERSION} \
    && rm -f /tmp/install-opentofu.sh \
    && tofu version

WORKDIR /workspaces