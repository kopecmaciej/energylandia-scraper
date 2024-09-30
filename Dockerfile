FROM python:3.12.3-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --upgrade pip --quiet

COPY main.py .

CMD ["python", "main.py"]
