FROM python:3.12-slim-bookworm
MAINTAINER Yury Yudkin <yudkin@gmail.com>

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python3", "bot/bot.py"]
