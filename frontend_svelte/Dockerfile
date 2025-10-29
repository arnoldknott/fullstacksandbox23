FROM node:24.6.0-alpine3.21 AS build
WORKDIR /app
COPY package*.json svelte.config.js ./
RUN npm install
COPY . .
# RUN printenv
# TBD: run in dev mode with npm run dev during development: separate build and dev stages!
RUN npm run build
# CMD ["sh" "-c"]

FROM node:24.6.0-alpine3.21
WORKDIR /app
# TBD: remove when error with internal ingres is fixed.
# RUN apk add --no-cache redis tcptraceroute
COPY --from=build /app/build /app/
COPY --from=build /app/package*.json /app/
# RUN ls -la /app
# TBD: make sure to only copy dependencies and not devDependencies - by runing the correct npm install command above.
# COPY --from=build /app/node_modules ./node_modules
RUN npm ci --omit=dev
# RUN ls -la /app/node_modules
RUN chown -R node:node /app
EXPOSE 80
# ENV PORT=80
USER node
CMD ["node", "/app/index.js"]
