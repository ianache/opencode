@echo off
REM Docker Compose setup script for GraphRAG Neo4j

echo Checking Docker installation...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check Docker Compose
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose is not available
    echo Please ensure Docker Desktop is running and includes Docker Compose
    pause
    exit /b 1
)

echo Docker installation found.
echo.

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo.
    echo IMPORTANT: Edit .env file with your Neo4j credentials
    echo Current default password is 'your_password_here' - please change it!
    echo.
    pause
)

echo Starting Neo4j container...
docker compose up -d

if errorlevel 1 (
    echo ERROR: Failed to start Neo4j container
    pause
    exit /b 1
)

echo.
echo Neo4j is starting up. This may take 30-60 seconds...
echo.

REM Wait and show status
timeout /t 10 /nobreak >nul
docker compose ps

echo.
echo Neo4j Browser will be available at: http://localhost:7474
echo Use credentials from your .env file to login.
echo.
echo To view logs: docker compose logs neo4j
echo To stop: docker compose down
echo.
pause