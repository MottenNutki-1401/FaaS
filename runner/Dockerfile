FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY runner.py .

# We don't copy functions here because they will be mounted from /mnt
# This makes the runner generic.

CMD ["python", "runner.py"]
