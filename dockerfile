# Dockerfile - production
FROM python:3.11-slim

WORKDIR /app

# system deps (if needed)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# copy
COPY . /app

# virtual env not necessary in container
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (Render uses PORT env var)
ENV PORT=8000
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --loop uvloop --http h11
