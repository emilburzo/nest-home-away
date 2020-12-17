#!/bin/bash

. .ci/constants.sh

docker pull ${IMAGE}
docker stop ${NAME}
docker rm ${NAME}
docker run -d --restart=always \
  -e NEST_ACCESS_TOKEN="${NEST_ACCESS_TOKEN}" \
  -e NEST_STRUCTURE="${NEST_STRUCTURE}" \
  -e NEST_USER="${NEST_USER}" \
  --name ${NAME} \
  -p ${PORT}:8080 \
  ${IMAGE}
