FROM python:3.11-slim-buster

WORKDIR /app

COPY src/bot_logic/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p src/bot_logic/logs

CMD ["python", "-m", "src.bot_logic.main.py"]