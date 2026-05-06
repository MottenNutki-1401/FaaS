FROM python:3.9-slim

WORKDIR /app

# Install docker CLI if needed, but we use the SDK
# We need to install some dependencies for the docker SDK to work if necessary
# but usually python-docker is enough as long as docker.sock is mounted.

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
