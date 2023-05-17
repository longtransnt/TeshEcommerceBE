# Use a Python 3.9 base image
FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /app

# Copy the requirements file to the app directory
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app files to the app directory
COPY . .

# Set the FLASK_APP environment variable
ENV FLASK_APP=app.py

# Expose port 5000 for the Flask app
EXPOSE 5000

# Start the Flask server
CMD ["flask", "run", "--host=0.0.0.0"]