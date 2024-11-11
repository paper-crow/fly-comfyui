#!/bin/bash
set -e

# Run the Python installer script in the background
(python3 download-models.py) &
echo "Model download process started in the background..."

# Execute the command passed from the Dockerfile immediately
exec "$@"
