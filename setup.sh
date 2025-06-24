#!/bin/bash

set -e

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH to current directory
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "Environment setup complete."
