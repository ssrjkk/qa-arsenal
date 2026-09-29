#!/bin/bash

set -e

echo "Запуск тестового окружения..."

export ENV=${ENV:-test}
export BASE_URL=${BASE_URL:-https://api.hh.ru}
export TIMEOUT=${TIMEOUT:-10}
export MAX_RETRIES=${MAX_RETRIES:-3}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo "Конфигурация:"
echo "  ENV: $ENV"
echo "  BASE_URL: $BASE_URL"
echo "  TIMEOUT: $TIMEOUT"
echo "  MAX_RETRIES: $MAX_RETRIES"
echo "  LOG_LEVEL: $LOG_LEVEL"

if [ "$1" = "lint" ]; then
    echo "Запуск линтеров..."
    ruff check .
    black --check .
    mypy api core models validators
    echo "Линтеры пройдены успешно"
    exit 0
fi

if [ "$1" = "test" ]; then
    shift
    echo "Запуск тестов..."
    python -m pytest tests/ -v --tb=short "$@"
    exit $?
fi

echo "Запуск тестов по умолчанию..."
python -m pytest tests/ -v --tb=short
