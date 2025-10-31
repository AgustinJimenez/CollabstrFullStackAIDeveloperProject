#!/bin/bash
# E2E Test Runner with configurable AI provider via .env files
# Usage: ./test-e2e.sh [test|ollama|openai] [test_name]

PROVIDER=${1:-test}
TEST_NAME=${2:-""}

echo "Running E2E tests with AI_PROVIDER=$PROVIDER"

# Stop existing containers
docker compose -f docker-compose.yml -f docker-compose.playwright.yml down

# Use appropriate .env file based on provider
case $PROVIDER in
    "test")
        echo "Using .env.test for fast testing"
        cp .env.test .env
        ;;
    "ollama")
        echo "Using .env with AI_PROVIDER=ollama"
        sed -i.bak 's/AI_PROVIDER=.*/AI_PROVIDER=ollama/' .env
        ;;
    "openai")
        echo "Using .env with AI_PROVIDER=openai"
        sed -i.bak 's/AI_PROVIDER=.*/AI_PROVIDER=openai/' .env
        ;;
    *)
        echo "Unknown provider: $PROVIDER. Using current .env"
        ;;
esac

# Start containers
docker compose -f docker-compose.yml -f docker-compose.playwright.yml up -d

# Wait for containers to be ready
echo "Waiting for containers to be ready..."
sleep 10

# Check health
echo "Checking Django health..."
docker compose -f docker-compose.yml -f docker-compose.playwright.yml exec django curl -s http://localhost:8000/api/health/ | grep -q "healthy" && echo "✅ Django is healthy" || echo "❌ Django not ready"

# Run tests
if [ -n "$TEST_NAME" ]; then
    echo "Running specific test: $TEST_NAME"
    docker compose -f docker-compose.yml -f docker-compose.playwright.yml exec django python -m pytest tests/test_e2e.py::TestAIBriefGenerator::$TEST_NAME --tb=short --browser chromium -v
else
    echo "Running all E2E tests"
    docker compose -f docker-compose.yml -f docker-compose.playwright.yml exec django python -m pytest tests/test_e2e.py --tb=short --browser chromium -v
fi

echo "E2E tests completed with AI_PROVIDER=$PROVIDER"