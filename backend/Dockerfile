# Official Python slim image 
FROM python:3.11.11-slim

# Setting the workdir in the container
WORKDIR /main

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && pip install --no-cache-dir --upgrade pip setuptools wheel \
&& pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the FastAPI app will run on
EXPOSE 8080

# Command to run the FastAPI app using Uvicorn
CMD ["python", "main.py"]