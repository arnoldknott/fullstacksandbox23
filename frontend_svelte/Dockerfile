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
EXPOSE 80
USER node
CMD ["node", "/app/index.js"]
