# TODO: maybe build the wheel inside docker, in another stage

FROM python:3-alpine

LABEL Name=karen Version=0.1.0

COPY dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp

CMD ["karen"]
