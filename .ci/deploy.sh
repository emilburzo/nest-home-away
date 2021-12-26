#!/bin/bash

. .ci/constants.sh

docker pull ${IMAGE}
docker stop ${NAME}
docker rm ${NAME}
docker run -d --restart=always \
  -e NEST_ACCESS_TOKEN="${NEST_ACCESS_TOKEN}" \
  -e NEST_STRUCTURE="${NEST_STRUCTURE}" \
  -e NEST_USER="${NEST_USER}" \
  -e NEST_REST_ENDPOINT="${NEST_REST_ENDPOINT}" \
  -e HOSTS="${HOSTS}" \
  -e WEBHOOK_OK_URL="${WEBHOOK_OK_URL}" \
  -e LOG_LEVEL="${LOG_LEVEL}" \
  -e TZ="${TZ}" \
  --name ${NAME} \
  ${IMAGE}
