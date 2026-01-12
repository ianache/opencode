#!/bin/bash

# Docker Compose setup script for GraphRAG Neo4j

echo "Checking Docker installation..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not available"
    echo "Please ensure Docker is running and includes Docker Compose"
    exit 1
fi

echo "Docker installation found."
echo

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo
    echo "IMPORTANT: Edit .env file with your Neo4j credentials"
    echo "Current default password is 'your_password_here' - please change it!"
    echo
fi

echo "Starting Neo4j container..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start Neo4j container"
    exit 1
fi

echo
echo "Neo4j is starting up. This may take 30-60 seconds..."
echo

# Wait and show status
sleep 10
docker compose ps

echo
echo "Neo4j Browser will be available at: http://localhost:7474"
echo "Use credentials from your .env file to login."
echo
echo "To view logs: docker compose logs neo4j"
echo "To stop: docker compose down"
echo