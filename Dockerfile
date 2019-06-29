FROM python:3-alpine as builder

WORKDIR /build
COPY . .

RUN pip wheel --wheel-dir dist --no-deps .
# RUN ls -la . dist

FROM python:3-alpine

COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp

CMD ["karen"]
