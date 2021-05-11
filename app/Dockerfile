# Use an official Python runtime as a parent image
FROM python:3.8-alpine3.10

# Make port 80 available to the world outside this container
EXPOSE 80

# Copy app files
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run __main__.py when the container launches
CMD python __main__.py