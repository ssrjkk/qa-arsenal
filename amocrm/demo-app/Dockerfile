FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask psycopg2-binary gunicorn

COPY app.py .

ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=amocrm
ENV DB_USER=user
ENV DB_PASSWORD=pass
ENV FLASK_APP=app.py

EXPOSE 8080

CMD ["python", "app.py"]