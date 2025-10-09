FROM python:3.13.0-alpine3.20 AS base
COPY . /app
WORKDIR /app
ENV PYTHONPATH="/app"
ENV VIRTUAL_ENV="/py"
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
EXPOSE 80

FROM base AS api_dev
RUN pip install --upgrade pip && \
    pip install -e .[dev]
# TBD: switch to log-level warning, when app is more mature:
# CMD ["uvicorn", "main:app", "--reload", "--log-level", "warning" ,"--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "main:app", "--reload" ,"--host", "0.0.0.0", "--port", "80"]

FROM base AS api_prod
LABEL org.opencontainers.image.source https://github.com/arnoldknott/fullstacksandbox23
RUN rm -rf tests/ .pytest_cache/ .vscode/ .git/ .github/ .gitignore README.md Dockerfile
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .
# TBD: consider running app with non-root user:
#     adduser --disabled-password --no-create-home backend-user
# USER backend-user
ARG COMMIT_SHA="noGitBuild"
ENV COMMIT_SHA=$COMMIT_SHA
# TBD: switch to log-level warning, when app is more mature:
# CMD ["uvicorn", "main:app", "--log-level", "warning", "--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]