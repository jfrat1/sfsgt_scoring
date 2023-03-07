#!/bin/bash

# This file will be used to run the scoring calculations
# and generate any required artifacts like scorint reports

EXEC_TIME=`date "+%Y-%m-%d %T"`
echo "Execution time: ${EXEC_TIME}"

BASEDIR=$(dirname $0)
echo "Script location: ${BASEDIR}"

PYTHON="${BASEDIR}/.venv/bin/python"
PY_FILE_PATH="${BASEDIR}/hello_world.py"

$PYTHON $PY_FILE_PATH
