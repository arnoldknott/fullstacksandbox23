FROM node:20.10.0-alpine3.19 AS build
WORKDIR /app
COPY package*.json svelte.config.js ./
RUN npm install
COPY . .
RUN npm run build
# CMD ["sh" "-c"]

FROM node:20-alpine3.17
COPY --from=build /app/build /app/
COPY --from=build /app/package*.json /app/
# TBD: make sure to only copy dependencies and not devDependencies
COPY --from=build /app/node_modules ./node_modules
EXPOSE 80
# ENV PORT=80
USER node
CMD ["node", "/app/index.js"]
