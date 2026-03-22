FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# JOB_TYPE 環境変数でバッチ種別を切り替える
# slack_batch / backlog_batch / webcrawl_batch
CMD ["python", "-m", "runner"]
