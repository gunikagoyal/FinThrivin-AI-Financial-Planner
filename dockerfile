# Use the official Python 3.11.9 slim-bullseye image from the Docker Hub
FROM python:3.11.9-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install dependencies and SQLite from source
RUN apt-get update && \
    apt-get install -y build-essential libssl-dev libffi-dev python3-dev wget && \
    wget https://www.sqlite.org/2023/sqlite-autoconf-3410200.tar.gz && \
    tar xzf sqlite-autoconf-3410200.tar.gz && \
    cd sqlite-autoconf-3410200 && \
    ./configure && make && make install && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* sqlite-autoconf-3410200.tar.gz sqlite-autoconf-3410200

# Create and set the working directory
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt --use-deprecated=legacy-resolver

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]