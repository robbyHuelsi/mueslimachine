# Use an official Python runtime as a parent image
FROM python:3.7-alpine

# Make port 80 available to the world outside this container
EXPOSE 80

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Run __init__.py when the container launches
COPY . /app
CMD python __init__.py