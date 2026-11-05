FROM python:3.13-slim

# No root inside the container: ground rule from the SecurityOps part.
RUN useradd --create-home --uid 1000 appuser
WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

USER appuser

# The platform dictates the port; locally the default applies.
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
