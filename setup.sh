#!/bin/bash

# This script sets up the mwSwap project.
# It creates a Python virtual environment, installs dependencies,
# and copies env.example to .env if the file does not exist.

set -e

# Determine python executable
PYTHON=${PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python is required but was not found. Please install Python 3." >&2
    exit 1
fi

# Create virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy env.example to .env if needed
if [ ! -f ".env" ] && [ -f "env.example" ]; then
    echo "Creating .env from env.example"
    cp env.example .env
fi

echo "Setup complete. Activate the environment with 'source .venv/bin/activate' and edit the .env file with your API keys."

