#!/bin/bash
# Diagnostic script to check database connection and tables

echo "=========================================="
echo "Database Diagnostic Script"
echo "=========================================="

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    exit 1
fi

echo "✓ DATABASE_URL is set"
echo "  (First 50 chars: ${DATABASE_URL:0:50}...)"

# Check Alembic connection
echo ""
echo "Checking Alembic connection..."
if alembic current; then
    echo "✓ Alembic can connect to database"
else
    echo "✗ Alembic cannot connect to database"
    exit 1
fi

# Show migration history
echo ""
echo "Migration history:"
alembic history | head -5

# Try to list tables (if psql is available)
echo ""
echo "Checking if psql is available..."
if command -v psql &> /dev/null; then
    echo "Listing tables in database:"
    psql "$DATABASE_URL" -c "\dt" 2>&1 || echo "Could not list tables (this is OK if psql client is not installed)"
else
    echo "psql not available (this is OK in container)"
fi

echo ""
echo "=========================================="
echo "Diagnostic complete"
echo "=========================================="

