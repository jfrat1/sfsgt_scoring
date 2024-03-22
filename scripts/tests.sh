#!/bin/sh

# Script to execute python tests on the sfsgt_scoring folder
# at the root of this repo. An HTML coverage report is automatically
# generated from teh pytest execution. Any commands which are passed
# to this script will be forwarded to the pytest command.
#
# Before executing this script, your python environment must have all
# required packages installed and must be activated (if using a virtual environment).

# Location to the folder containing this script
SCRIPT_DIR_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

REPO_ROOT="${SCRIPT_DIR_PATH}/.."
PYTHON_SOURCE_PATH="${REPO_ROOT}/sfsgt_scoring"

set -x
export PYTHONPATH="${PYTHONPATH}:${REPO_ROOT}"
pytest "$PYTHON_SOURCE_PATH" --cov="$PYTHON_SOURCE_PATH" --cov-report=html "$@"
