#!/bin/bash
# Setup script for Samsung WAM Controller on Linux

echo "Samsung WAM Controller Setup"
echo "============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.6+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "Installing required Python packages..."
pip3 install -r requirements.txt

echo "Setup complete! You can now use the Samsung WAM Controller."
echo ""
echo "Examples:"
echo "  Discover speakers: python3 wam_cli.py discover"
echo "  List speakers: python3 wam_cli.py list"
echo "  Set volume: python3 wam_cli.py volume 'Speaker Name' 15"
echo ""
echo "See README.md for full documentation."