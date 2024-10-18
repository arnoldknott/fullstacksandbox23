FROM ghcr.io/opentofu/opentofu:1.8.2
WORKDIR /src
RUN apk add --no-cache --update python3 py3-pip 
RUN apk add --no-cache --update --virtual=build gcc musl-dev python3-dev libffi-dev openssl-dev cargo make && pip3 install --no-cache-dir --prefer-binary azure-cli && apk del build
COPY . .
# EXPOSE 443
# RUN "tofu -version"
# ENTRYPOINT [ "./deploy.sh" ]
# CMD [ "tofu", "-version" ]
# CMD [ "--version" ]