
FROM python:3.9

WORKDIR /code

COPY requirements.txt .

# Disabling the use of the cache directory for package retrieval
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory (with Django source files) to the current working directory (/backend) in the container
COPY . .