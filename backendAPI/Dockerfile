FROM python:3.10-alpine as base
COPY . /app
WORKDIR /app
ENV VIRTUAL_ENV=/py
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

FROM base as dev
EXPOSE 8660
RUN pip install  --upgrade pip && \
    pip install -e .[dev]
    # following install only needed for building psycopg2:
    # TBD: add when adding database:
    # apk add --update --no-cache --virtual .tmp-build-deps \
    #     build-base postgresql-dev musl-dev && \
    # TBD: change user running the app in production
#     adduser \
#         --disabled-password \
#         --no-create-home \
#         backend-user
# USER backend-user
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8660"]

# TBD - add prod stage