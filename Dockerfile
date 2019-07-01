FROM python:3-alpine AS builder

ENV PIP_NO_CACHE_DIR=1
WORKDIR /build

# https://github.com/sdispater/poetry/issues/1179
RUN pip install "poetry==1.0.0a4" \
    && mkdir -p ~/.config/pypoetry \
    && poetry config settings.virtualenvs.create false

# No need for layer-caching here
# as `poetry export` is supposed to be a cheap operation.

COPY . .
RUN poetry export -n -f requirements.txt \
    && poetry build -n -f wheel

# RUN pip wheel -r requirements.txt --wheel-dir dist
# RUN ls -laR

FROM python:3-alpine

ENV PIP_NO_CACHE_DIR=1
WORKDIR /app

# Cache dependencies in a separate layer
# that rebuilds only when `requirements.txt` is changed
COPY --from=builder /build/requirements.txt ./
RUN pip install -r requirements.txt

# Install the app
COPY --from=builder /build/dist/*.whl /tmp/wheels/
RUN pip install --no-index --find-links /tmp/wheels karen && rm -rf /tmp

CMD ["karen"]
