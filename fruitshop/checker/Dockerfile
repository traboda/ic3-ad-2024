FROM python:3.12

RUN python -m pip install --upgrade pip

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir /app
WORKDIR /app

ENV PYTHONUNBUFFERED=TRUE
ENV PWNLIB_NOTERM=true

COPY auth.so /app/
COPY functions_order.json /app/
COPY verify.py /app/
COPY bi0stools.py /app/
COPY proto /app/proto/
COPY server.py /app/
COPY uv.lock /app/
COPY pyproject.toml /app/
RUN uv run python -m grpc_tools.protoc -I /app/proto/ --python_out=. --grpc_python_out=. checker.proto
ENV PWNLIB_NOTERM=true

EXPOSE 50051
ENTRYPOINT ["uv","run", "/app/server.py"]
