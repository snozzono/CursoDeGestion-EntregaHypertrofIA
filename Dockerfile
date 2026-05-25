FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY .env .

RUN mkdir -p logs data/processed

CMD ["python", "src/1_ingest.py"]