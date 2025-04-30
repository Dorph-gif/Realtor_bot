FROM python:3.11-slim-buster

WORKDIR /app

COPY src/database_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8005

CMD ["uvicorn", "src.database_service.main:app", "--host", "0.0.0.0", "--port", "8005"]