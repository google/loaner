#!/bin/bash
#
# Execute frontend and Chrome app npm tests.
#   Usage: ./angular_tests.sh

set -e

cd loaner

# Install node modules.
npm install

# Run frontend build.
npm run build:frontend
# Cleanup compiled files to prevent the disk from filling.
rm -r web_app/frontend/dist

# Run chrome app build.
npm run build:chromeapp:once
# Cleanup compiled files to prevent the disk from filling.
rm -r chrome_app/dist

# Run chrome app and frontend tests.
npm run test:once
