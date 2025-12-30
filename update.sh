#!/bin/bash
# Update script for Affidavit Writing Assistant (Mac/Linux)

echo "========================================"
echo "  Affidavit Assistant - Update"
echo "========================================"
echo

echo "Pulling latest changes from GitHub..."
git pull

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Failed to pull updates from GitHub"
    echo "Make sure you have internet connection and git is configured"
    exit 1
fi

echo
echo "Update complete!"
echo

echo "Checking for dependency updates..."

# Activate virtual environment and update dependencies
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    echo "Dependencies updated."
    deactivate
else
    echo "Note: Virtual environment not found. Run setup first."
fi

echo
echo "========================================"
echo "  Update finished successfully!"
echo "========================================"
echo
