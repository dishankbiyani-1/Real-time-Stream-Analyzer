FROM python:3.11-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install additional Python dependencies
COPY requirements.txt /code/requirements.txt

RUN pip install torch==2.3.0 
RUN pip install -r /code/requirements.txt

# Set working directory and copy project files
WORKDIR /code
COPY . .
