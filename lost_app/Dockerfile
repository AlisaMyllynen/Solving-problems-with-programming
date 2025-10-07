FROM python:3.11-slim
WORKDIR /app

# Install build deps for any packages (none heavy here) and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 5000

ENV FLASK_RUN_HOST=0.0.0.0
CMD ["python", "app.py"]
