FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py build_frontend.py ./
COPY static ./static

# Données persistantes si un volume est monté (sinon créées au démarrage)
VOLUME ["/app/data"]

EXPOSE 8000
ENV PORT=8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "server:app"]
