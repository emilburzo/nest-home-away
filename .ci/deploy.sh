#!/bin/bash

. .ci/constants.sh

docker pull ${IMAGE}
docker stop ${NAME}
docker rm ${NAME}
docker run -d --restart=always --name ${NAME} -p ${PORT}:8080 ${IMAGE}
