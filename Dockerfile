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

# Copy the current directory contents into the container
COPY . .

# Expose the desired port
EXPOSE 8765

# Run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8765"]
