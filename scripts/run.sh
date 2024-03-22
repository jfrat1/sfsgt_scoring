#!/bin/bash

# This file will be used to run the scoring calculations
# and generate any required artifacts like scorint reports

EXEC_TIME=`date "+%Y-%m-%d %T"`
echo "Execution time: ${EXEC_TIME}"

# This is the absolute path to the directory where this shell scrips is located
# NOTE - requires that we're running in bash, so the files must include the !/bin/bash shebang line
BASE_DIR_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

PYTHON="${BASE_DIR_PATH}/.venv/bin/python"
PY_FILE_PATH="${BASE_DIR_PATH}/python/season_2023.py"

echo "Executing: $PY_FILE_PATH"``

$PYTHON $PY_FILE_PATH
