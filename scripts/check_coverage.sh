#!/bin/bash
# Script to check test coverage excluding integration tests

# Create directory for the script
mkdir -p scripts

# Make sure the script is executable
chmod +x scripts/check_coverage.sh

# Run the tests with coverage, excluding integration tests
python -m pytest -k "not integration" --cov=niceboard/ --cov-report=term --cov-report=html:coverage_report

echo "Coverage report generated in coverage_report directory"
echo "Open coverage_report/index.html to view the detailed report"