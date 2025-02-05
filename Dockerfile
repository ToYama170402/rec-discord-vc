# Use the official Python image from the Docker Hub
FROM python:3.9-slim

RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /workspace

# Copy the current directory contents into the container at /app
COPY . /workspace

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["python", "app.py"]