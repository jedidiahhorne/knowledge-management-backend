#!/bin/bash
# Combined lint and test script

set -e

echo "=== Running Linter ==="
./scripts/lint.sh

echo ""
echo "=== Running Tests ==="
./scripts/test.sh

echo ""
echo "=== All checks passed! ==="

