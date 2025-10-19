# Railway Dockerfile that uses docker-compose
FROM docker/compose:latest

# Install docker-compose
RUN apk add --no-cache docker-compose

# Copy the entire project
COPY . /app
WORKDIR /app

# Make sure docker-compose is available
RUN chmod +x /usr/local/bin/docker-compose

# Start the services
CMD ["docker-compose", "up"]
