# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy the local code to the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port on which the Django app will run
EXPOSE 8000

# Command to run on container start
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "dockerfile_publisher.wsgi:application"]