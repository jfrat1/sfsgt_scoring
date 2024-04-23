#!/bin/sh

# Script to execute the sfsgt_scoring CLI. Commands to the CLi should be added as additional
# commands to this script. They will be passed on verbatim.
#
# Before executing this script, your python environment must have all
# required packages installed and must be activated (if using a virtual environment).

# Location to the folder containing this script
SCRIPT_DIR_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

REPO_ROOT="${SCRIPT_DIR_PATH}/.."
PYTHON_SOURCE_PATH="${REPO_ROOT}/sfsgt_scoring"

set -x
export PYTHONPATH="${PYTHONPATH}:${REPO_ROOT}"
python """$PYTHON_SOURCE_PATH/cli/run_sfsgt_scoring.py""" "$@"
