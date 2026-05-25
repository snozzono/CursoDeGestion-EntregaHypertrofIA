FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/raw/ ./data/raw/
COPY .env .

RUN mkdir -p logs data/processed data/errors

CMD ["python", "src/pipeline.py"]