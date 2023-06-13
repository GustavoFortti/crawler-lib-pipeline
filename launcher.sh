#!/bin/bash

LOCAL=$(pwd)/project

source $LOCAL/config/env.sh

ENV=$1
JOB_NAME=$2
DRIVER=$3
DRIVER_PATH=$4
MASTER=$5

echo $ENV
echo $JOB_NAME
echo $DRIVER
echo $DRIVER_PATH
echo $MASTER

# source $LOCAL/shared/scripts/logger.sh
source $LOCAL/config/setup.sh

if [[ "$DRIVER" != "local-selenium" ]]; then
    install_pip
    install_from_requirements "$LOCAL/config/requirements-sys.txt" "install_sys"
    install_from_requirements "$LOCAL/config/requirements-py.txt" "install_lib"
fi

echo "--env "$ENV" --job_name "$JOB_NAME" --driver "$DRIVER" --driver_path "$DRIVER_PATH" --master "$MASTER""
python3 $LOCAL/main.py --env "$ENV" --job_name "$JOB_NAME" --driver "$DRIVER" --driver_path "$DRIVER_PATH" --master "$MASTER"