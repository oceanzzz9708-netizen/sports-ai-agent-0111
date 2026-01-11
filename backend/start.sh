#!/bin/bash
echo "Starting AI Agent API..."
python -c "import sys; print(f'Python {sys.version}')"
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60
