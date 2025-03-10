#!/bin/bash
# Script to run integration tests

# Make sure environmental variables are set
if [ -z "$NICEBOARD_API_KEY" ]; then
    echo "Error: NICEBOARD_API_KEY environment variable must be set"
    exit 1
fi

# Optionally check for base URL
if [ -z "$NICEBOARD_BASE_URL" ]; then
    echo "Warning: NICEBOARD_BASE_URL not set, using default"
fi

# Run only the integration tests
python -m pytest -v -m integration
