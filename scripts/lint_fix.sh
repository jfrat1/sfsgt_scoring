#!/bin/sh

# Run all fix commands and accumulate exit codes
exit_code=0

echo "Running ruff format..."
if ! ruff format; then
    echo "❌ ruff format failed"
    exit_code=1
else
    echo "✅ ruff format completed"
fi

echo "Running ruff check --select I --fix..."
if ! ruff check --select I --fix; then
    echo "❌ ruff import fix failed"
    exit_code=1
else
    echo "✅ ruff import fix completed"
fi

echo "Running ruff check --fix..."
if ! ruff check --fix; then
    echo "❌ ruff check --fix failed"
    exit_code=1
else
    echo "✅ ruff check --fix completed"
fi

exit $exit_code