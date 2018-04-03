#!/bin/bash
#
# Execute frontend and Chrome app npm tests.
#   Usage: ./angular_tests.sh

set -ex

npm install
npm run test:once
