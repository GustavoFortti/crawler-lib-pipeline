#!/bin/bash

LOCAL=$(pwd)/project

source $LOCAL/config/env.sh

args=(
    "--env" "$1"
    "--job_name" "$2"
    "--job_exec_type" "$3"
    "--driver" "$4"
    "--driver_path" "$5"
    "--master" "$6"
    "--uri" "$7"
)
# source $LOCAL/shared/scripts/logger.sh
source $LOCAL/config/setup.sh

if [[ "$DRIVER" != "local-selenium" ]]; then
    install_pip
    install_from_requirements "$LOCAL/config/requirements-sys.txt" "install_sys"
    install_from_requirements "$LOCAL/config/requirements-py.txt" "install_lib"
fi

echo "${args[@]}"
python3 "$LOCAL/main.py" "${args[@]}"