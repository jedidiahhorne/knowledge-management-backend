#!/bin/bash
# Test script for the knowledge management backend

set -e

echo "Running pytest..."
pytest tests/ -v

echo "Tests completed successfully!"

