#!/bin/bash

DOCKER_REPO=mghpcc
TAG=latest
#LOCAL_CONFIG_DIR=/home/jculbert/s3_response_time/config
LOCAL_CONFIG_DIR=/Users/culbertj/Development/python/s3-response-time/docker/configs
CONTAINER_CONFIG_DIR=/config
IMAGE=$DOCKER_REPO/s3_response_time:$TAG

for cred in $LOCAL_CONFIG_DIR/*.json; do
  echo $(basename -- $cred)
  docker run --rm --volume $LOCAL_CONFIG_DIR:$CONTAINER_CONFIG_DIR $IMAGE $CONTAINER_CONFIG_DIR/$(basename -- $cred)
done

