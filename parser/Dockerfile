FROM python:3.13.3-alpine AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .
RUN chown -R appuser:appuser .  && chmod -R 1777 .
USER appuser
EXPOSE 5000

FROM base AS test
CMD [ "python", "-m" , "flask", "run", "--debug", "--host=0.0.0.0"]

FROM base AS prod
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]