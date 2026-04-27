#!/bin/bash

echo "============================================"
echo "🚀 Starting TMPS Movie Bot"
echo "============================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the bot
python main.py

