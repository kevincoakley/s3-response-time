FROM  python:3.12-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir /code /config
WORKDIR /code

COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen --no-dev --no-cache
ENV PATH="/code/.venv/bin:$PATH"
ENTRYPOINT ["python3", "/code/s3_response_time.py", "-c"]

COPY s3_response_time.py pyproject.toml uv.lock /code/


