FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./wait-for-it.sh

CMD ["/wait-for-it.sh", "db", "gunicorn --bind 0.0.0.0:8000 jobportal.wsgi:application"]
