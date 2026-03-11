FROM python:3.14.3-alpine3.23 AS base
COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/
COPY . /app
WORKDIR /app
ENV PYTHONPATH="/app"
ENV VIRTUAL_ENV="/py"
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
EXPOSE 80

FROM base AS api_dev
RUN uv sync --frozen --extra dev
# TBD: switch to log-level warning, when app is more mature:
# CMD ["uvicorn", "main:app", "--reload", "--log-level", "warning" ,"--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "main:fastapi_app", "--reload", "--no-access-log", "--host", "0.0.0.0", "--port", "80"]

FROM base AS api_prod
LABEL org.opencontainers.image.source https://github.com/arnoldknott/fullstacksandbox23
RUN rm -rf tests/ .pytest_cache/ .vscode/ .git/ .github/ .gitignore README.md Dockerfile
RUN uv sync --frozen --no-dev --no-cache
# TBD: consider running app with non-root user:
#     adduser --disabled-password --no-create-home backend-user
# USER backend-user
ARG COMMIT_SHA="noGitBuild"
ENV COMMIT_SHA=$COMMIT_SHA
# TBD: switch to log-level warning, when app is more mature:
# CMD ["uvicorn", "main:app", "--log-level", "warning", "--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "main:fastapi_app", "--no-access-log", "--host", "0.0.0.0", "--port", "80"]


FROM base AS worker_dev
RUN uv sync --frozen --extra dev && \
    adduser -D -H worker
USER worker
CMD ["celery", "-A", "core.celery_app:celery_app", "worker", "--loglevel=info"]

FROM base AS worker_prod
LABEL org.opencontainers.image.source https://github.com/arnoldknott/fullstacksandbox23
RUN rm -rf tests/ .pytest_cache/ .vscode/ .git/ .github/ .gitignore README.md Dockerfile
RUN uv sync --frozen --no-dev --no-cache && \
    adduser -D -H worker
USER worker
ARG COMMIT_SHA="noGitBuild"
ENV COMMIT_SHA=$COMMIT_SHA
CMD ["celery", "-A", "core.celery_app:celery_app", "worker", "--loglevel=warning"]