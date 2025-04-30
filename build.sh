#!/usr/bin/env bash

#
# CONSTANTS
#

SCRIPT_PATH="$(realpath "$0")"
PROJECT_DIR="$(dirname "${SCRIPT_PATH:?}")"

#
# FUNCTIONS
#

function check_requirement(){
    if ! eval "$@" >> /dev/null 2>&1 ; then
        echo "! Fatal : missing requirement"
        if [ -n "${*: -1}" ]; then echo "${@: -1}"; fi
        exit 1
    fi
}

function init_build(){
    cd "${PROJECT_DIR}" || exit
    echo ". Build environment :"
    poetry env info
    poetry check
    echo ". Install dependencies"
    poetry run python -m pip install --upgrade pip
    poetry update
}

function openapi_generation() {
    echo ". Dump OpenAPI v3 specification"
    cd "${PROJECT_DIR}" || exit
    poetry run python ./sslamanagerrest/__main__.py --dump-openapi -c /dev/null
}

function build(){
    echo ". Build"
    cd "${PROJECT_DIR}" || exit
    rm -rf "${PROJECT_DIR}/dist"
    poetry build

    echo ". Built in dist/:"
    ls "./dist/"
}

#
# MAIN
#

check_requirement poetry --version "! Install poetry first"

init_build
xsdata_generation
openapi_generation
build

echo ". OK"
exit 0


