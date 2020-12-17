#!/bin/bash

set -eu

. .ci/constants.sh

docker build -t ${IMAGE} .
docker push ${IMAGE}