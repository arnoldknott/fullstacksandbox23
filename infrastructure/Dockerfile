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
RUN curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh && \
    chmod +x install-opentofu.sh
RUN apk add gpg gpg-agent
RUN ./install-opentofu.sh --install-method standalone --install-path /usr/local/bin --opentofu-version 1.10.6

# Install Azure-CLI in container.
RUN apk add --no-cache --update python3 py3-pip 
RUN apk add --no-cache --update --virtual=build gcc musl-dev python3-dev libffi-dev openssl-dev cargo make && pip3 install --no-cache-dir --prefer-binary azure-cli && apk del build

# add app infrastructure source code
WORKDIR /src
COPY . .
