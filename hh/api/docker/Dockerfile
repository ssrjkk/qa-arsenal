FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV CI=true
ENV BASE_URL=https://api.hh.ru
ENV TIMEOUT=30

CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "-m", "not slow"]
