# check=skip=InvalidDefaultArgInFrom
ARG NODE_VERSION
ARG ALPINE_VERSION
ARG BUN_VERSION

FROM node:${NODE_VERSION}-alpine${ALPINE_VERSION} AS setup
ARG BUN_VERSION
WORKDIR /app
RUN npm install -g bun@${BUN_VERSION}

FROM setup AS dev
RUN apk add --no-cache docker-cli git

FROM dev AS test
COPY package.json bun.lock svelte.config.js ./
RUN bun install --frozen-lockfile

FROM test AS build
COPY . .
RUN bun run build

FROM setup
COPY --from=build /app/build /app/
COPY --from=build /app/package*.json /app/bun.lock /app/
RUN bun install --frozen-lockfile --production
RUN chown -R node:node /app
EXPOSE 80
USER node
CMD ["bun", "/app/index.js"]
