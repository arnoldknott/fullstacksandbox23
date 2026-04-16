FROM node:24.14.0-alpine3.23 AS setup
WORKDIR /app
RUN npm install -g bun

FROM setup As test
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
