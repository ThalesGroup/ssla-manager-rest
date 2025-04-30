#!/usr/bin/env bash

#
# CONSTANTS
#
SCRIPT_PATH="$(realpath "$0")"
PROJECT_DIR="$(dirname "${SCRIPT_PATH}")"

#
# MAIN
#

echo ". Install Security Policy Manager API 'sslamanagerrest' module"
cd "${PROJECT_DIR}" || exit
wheel="$(find "./dist/" -type f -name "*.whl")"
poetry run python -m pip install "${wheel}" --force-reinstall

echo ". OK"
exit 0
