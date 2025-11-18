#!/bin/bash
# Lint script for the knowledge management backend

set -e

echo "Running ruff linter..."
ruff check app tests

echo "Linting completed successfully!"

