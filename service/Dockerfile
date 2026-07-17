FROM python:3.11-alpine AS requirements-stage

WORKDIR /app

RUN pip install --no-cache-dir poetry \
    && poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim AS final-stage

WORKDIR /core

COPY --from=requirements-stage /app/requirements.txt /core/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /core/requirements.txt \
    && rm -rf /root/.cache /usr/share/locale/*

COPY ./ /core/

RUN find . -name "*.pyc" -exec rm -f {} \;

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
