FROM python:3.13-slim

# Kein Root im Container: Grundregel aus dem SecurityOps-Teil.
RUN useradd --create-home --uid 1000 appuser
WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

USER appuser

# Die Plattform gibt den Port vor; lokal gilt der Default.
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
