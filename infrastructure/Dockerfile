# ==== using old method ===
# # TBD: from tofu 1.10 the opentofu image cannot be used as a base image
# # for building custom images
# # last version that supports that is 1.9.4
# FROM ghcr.io/opentofu/opentofu:1.19.4
# WORKDIR /src
# # Install Azure-CLI in container.
# RUN apk add --no-cache --update python3 py3-pip 
# RUN apk add --no-cache --update --virtual=build gcc musl-dev python3-dev libffi-dev openssl-dev cargo make && pip3 install --no-cache-dir --prefer-binary azure-cli && apk del build
# COPY --from=tofu /usr/local/bin/tofu /usr/local/bin/tofu
# COPY . .
# # EXPOSE 443
# # RUN "tofu -version"
# # ENTRYPOINT [ "./deploy.sh" ]
# # CMD [ "tofu", "-version" ]
# # CMD [ "--version" ]

# # ==== starting with tofu-minimal and azure-cli image method ===
# FROM ghcr.io/opentofu/opentofu:1.10.6-minimal as tofu
# FROM mcr.microsoft.com/azure-cli:2.77.0
# WORKDIR /src
# # Install Azure-CLI in container.
# # RUN apk add --no-cache --update python3 py3-pip 
# # RUN apk add --no-cache --update --virtual=build gcc musl-dev python3-dev libffi-dev openssl-dev cargo make && pip3 install --no-cache-dir --prefer-binary azure-cli && apk del build
# COPY --from=tofu /usr/local/bin/tofu /usr/local/bin/tofu
# COPY . .

FROM alpine:3.22.1
# Get installation script

ARG OPENTOFU_VERSION=1.11.1

# Get installation script and install OpenTofu (standalone)
RUN apk add --no-cache ca-certificates curl gnupg bash && \
    update-ca-certificates && \
    curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh && \
    chmod +x install-opentofu.sh && \
    ./install-opentofu.sh --install-method standalone --opentofu-version ${OPENTOFU_VERSION} && \
    tofu version

# Install Azure CLI inside a virtualenv to avoid PEP 668 (externally managed env)
RUN apk add --no-cache --update python3 py3-pip && \
    python3 -m venv /opt/az && \
    . /opt/az/bin/activate && \
    pip install -U pip setuptools wheel && \
    apk add --no-cache --update --virtual=build gcc musl-dev python3-dev libffi-dev openssl-dev cargo make && \
    pip install --no-cache-dir --prefer-binary azure-cli && \
    apk del build && \
    ln -sf /opt/az/bin/az /usr/local/bin/az

# add app infrastructure source code
WORKDIR /src
COPY . .
