# Use an official Python runtime as a parent image
FROM python:3.10-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /telnyx-chatbot

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir git+https://github.com/pipecat-ai/pipecat.git

# Create static directory and ensure it exists
RUN mkdir -p static

# Copy the static files first
COPY static/* static/

# Copy the rest of the application
COPY . .

# Verify the audio file exists (will fail build if missing)
RUN test -f static/office-ambience.mp3 || (echo "office-ambience.mp3 not found in static directory" && exit 1)

# Expose the desired port
EXPOSE 8765

# Run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8765"]
