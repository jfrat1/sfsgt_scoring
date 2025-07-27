#!/bin/sh

# Run all commands and accumulate exit codes
exit_code=0

echo "Running ruff format check..."
if ! ruff format --check; then
    echo "❌ ruff format check failed"
    exit_code=1
else
    echo "✅ ruff format check passed"
fi

echo "Running ruff check..."
if ! ruff check; then
    echo "❌ ruff check failed"
    exit_code=1
else
    echo "✅ ruff check passed"
fi

echo "Running mypy..."
if ! mypy .; then
    echo "❌ mypy check failed"
    exit_code=1
else
    echo "✅ mypy check passed"
fi

exit $exit_code