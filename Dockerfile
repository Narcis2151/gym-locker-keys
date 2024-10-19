# Use the official lightweight Python image.
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED True

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0

# Install tesseract if you're using pytesseract
# RUN apt-get install -y tesseract-ocr

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Streamlit default port is 8501)
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
