FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY bot.py config.py compressor.py queue_manager.py utils.py .

# Create downloads directory
RUN mkdir -p downloads

# Run bot
CMD ["python", "bot.py"]
