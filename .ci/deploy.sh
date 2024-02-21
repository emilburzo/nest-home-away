#!/bin/bash

SHORT_SHA="$(git rev-parse --short HEAD)"
echo "SHORT_SHA=${SHORT_SHA}"
cat .ci/deploy.yaml | sed "s/SHORT_SHA/${SHORT_SHA}/g" | kubectl apply -f -
