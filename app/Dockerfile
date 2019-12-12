# Use an official Python runtime as a parent image
FROM python:3.8-alpine3.10

# Make port 80 available to the world outside this container
EXPOSE 80

# Set the working directory to /app
WORKDIR /app

# Install mySQL client (https://hub.docker.com/r/tnir/mysqlclient/dockerfile)
RUN apk add --update --no-cache mariadb-connector-c-dev \
	&& apk add --no-cache --virtual .build-deps \
		mariadb-dev \
		gcc \
		musl-dev \
	&& pip install mysqlclient==1.4.5 \
	&& apk del .build-deps

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Run __init__.py when the container launches
COPY . /app
CMD python __init__.py