#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if tkinter is installed
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter is not installed. Please install it first using your package manager."
    echo "For example on Arch Linux: sudo pacman -S python-tkinter"
    echo "Or on Debian/Ubuntu: sudo apt install python3-tk"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with system-site-packages..."
    python3 -m venv venv --system-site-packages
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
pip install pystray gitpython

echo "Setup completed successfully!"
echo "You can now run the application using ./run.sh" 