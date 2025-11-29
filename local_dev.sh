#!/bin/bash

# Local Development Script for Issue #12 MVP
# Starts both backend and frontend in parallel for local testing

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Kinemotion Issue #12: Local Dev Setup${NC}"
echo -e "${BLUE}========================================${NC}"

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv not found. Install from https://github.com/astral-sh/uv${NC}"
    exit 1
fi

echo -e "${GREEN}✓ uv installed${NC}"

if ! command -v yarn &> /dev/null; then
    echo -e "${RED}❌ Yarn not found. Run: npm install -g yarn${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Yarn installed${NC}"

# Backend setup
echo -e "\n${YELLOW}Setting up backend...${NC}"

if [ ! -d "$BACKEND_DIR/venv" ] && [ ! -f "$BACKEND_DIR/uv.lock" ]; then
    echo "Installing backend dependencies..."
    cd "$BACKEND_DIR"
    uv sync
else
    echo -e "${GREEN}✓ Backend dependencies already installed${NC}"
fi

# Backend environment
if [ ! -f "$BACKEND_DIR/.env.local" ]; then
    echo "Creating .env.local for backend..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env.local"
    echo -e "${YELLOW}Note: R2 variables left empty (optional for testing)${NC}"
fi

# Frontend setup
echo -e "\n${YELLOW}Setting up frontend...${NC}"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    yarn install
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

# Frontend environment
if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
    echo "Creating .env.local for frontend..."
    cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env.local"

    # Set API URL
    echo "VITE_API_URL=http://localhost:8000" >> "$FRONTEND_DIR/.env.local"
    echo -e "${GREEN}✓ Set VITE_API_URL=http://localhost:8000${NC}"
fi

# Start services
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Starting services...${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${BLUE}Backend:  http://localhost:8000${NC}"
echo -e "${BLUE}Frontend: http://localhost:5173${NC}"
echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"

echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Create a temporary directory for PIDs
PID_DIR=$(mktemp -d)
trap "rm -rf $PID_DIR" EXIT

# Function to handle cleanup
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"

    if [ -f "$PID_DIR/backend.pid" ]; then
        kill $(cat "$PID_DIR/backend.pid") 2>/dev/null || true
    fi
    if [ -f "$PID_DIR/frontend.pid" ]; then
        kill $(cat "$PID_DIR/frontend.pid") 2>/dev/null || true
    fi

    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${BLUE}[Backend] Starting...${NC}"
cd "$BACKEND_DIR"
uv run python -m uvicorn src.kinemotion_backend.app:app --reload --host 0.0.0.0 --port 8000 > /tmp/kinemotion_backend.log 2>&1 &
echo $! > "$PID_DIR/backend.pid"

# Wait for backend to be ready
echo -e "${YELLOW}[Backend] Waiting to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}[Backend] ✓ Ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}[Backend] ✗ Failed to start${NC}"
        cat /tmp/kinemotion_backend.log
        exit 1
    fi
    sleep 1
done

# Start frontend
echo -e "${BLUE}[Frontend] Starting...${NC}"
cd "$FRONTEND_DIR"
yarn dev > /tmp/kinemotion_frontend.log 2>&1 &
echo $! > "$PID_DIR/frontend.pid"

# Wait for frontend to be ready
echo -e "${YELLOW}[Frontend] Waiting to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}[Frontend] ✓ Ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}[Frontend] Note: May take a moment to fully load${NC}"
        break
    fi
    sleep 1
done

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Both services are running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Open http://localhost:5173 in your browser"
echo "2. Upload a CMJ or Drop Jump video"
echo "3. See real metrics appear!"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "Backend:  tail -f /tmp/kinemotion_backend.log"
echo "Frontend: tail -f /tmp/kinemotion_frontend.log"
echo ""

# Wait for both processes
wait
