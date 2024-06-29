#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

# Activate the virtual environment
source "venv/bin/activate"

# Run your Python script (replace 'your_script.py' with your actual script name)
python3 main.py
