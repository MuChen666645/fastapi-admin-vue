FROM python:3.11.11-alpine3.21 AS requirements-stage

WORKDIR /app

RUN pip install --no-cache-dir poetry \
    && poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11.11-slim-bookworm AS final-stage

WORKDIR /core

COPY --from=requirements-stage /app/requirements.txt /core/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /core/requirements.txt \
    && rm -rf /root/.cache /usr/share/locale/* \
    && useradd --system --uid 10001 --create-home --home-dir /home/app app \
    && mkdir -p /core/uploads \
    && chown -R app:app /core /home/app

COPY ./ /core/

RUN find . -name "*.pyc" -exec rm -f {} \;

USER app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
