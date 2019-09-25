#!/bin/bash
#
# Grab n Go Loaner deployment script.

# Include guard to prevent this script from being imported more than once.
if [[ -z "${DEPLOY_SH__}" ]]; then
  readonly DEPLOY_SH__=1

  set -e

  # Everything between the '#' blocks is configurable by individual
  # implementers. The rest is configured to work with the existing python
  # deployment implementation.
  ##############################################################################
  # Set to false if you want to skip the binary checks.
  BINARY_CHECK=true

  # Set to false if you want to skip the gcloud auth check.
  GCLOUD_AUTH_CHECK=true

  # Deployment environments; set these to your Google Cloud Project ID's.
  # These should take the format of type=project where name is the second
  # argument passed during invocation and project is the Google Cloud Project
  # ID to deploy to.
  # e.g. "dev=loaner-dev" and "prod=loaner."
  # NOTE: LOCAL does not need to be changed, it is prepared for you.
  LOCAL="local=dev"
  DEV="dev=loaner-dev"
  QA="qa=loaner-qa"
  PROD="prod=loaner-prod"

  # The app server definitions in a comma separated list.
  # NOTE: All of the deployment environments defined above need to be in this
  # list, should you remove one from above so should you remove it from here.
  readonly APP_SERVERS="${LOCAL},${DEV},${QA},${PROD}"

  # The app engine services to deploy as configured by the following yaml files.
  # The defaults are: "app.yaml,endpoints.yaml,chrome.yaml,action_system.yaml"
  readonly SERVICES="app.yaml,endpoints.yaml,chrome.yaml,action_system.yaml"

  # App Engine configuration files.
  readonly CONFIGS="cron.yaml,index.yaml,queue.yaml"

  # The web_app directory relative to the Bazel WORKSPACE.
  # The default is: "loaner/web_app"
  readonly WEB_APP_DIR="loaner/web_app"

  # The chrome_app directory relative to the Bazel WORKSPACE.
  # The default is: "loaner/chrome_app"
  readonly CHROME_APP_DIR="loaner/chrome_app"

  # The BUILD target defined in the loaner_appengine_binary BUILD rule found in
  # the web_app directory BUILD file.
  # The default is: "runfiles"
  readonly BUILD_TARGET="runfiles"
  ##############################################################################

  # Color definitions for messages.
  readonly _RED="\x1B[31m"
  readonly _GREEN="\x1B[32m"
  readonly _RESET="\x1B[0m"

  # Platform definitions.
  readonly _LINUX="Linux"
  readonly _MAC="Mac"

  # Displays an error message and exits.
  # @param {string} the error message to display before exit.
  function error_message() {
    [[ -z "${1}" ]] && echo "error_message requires one argument."
    echo -e "${_RED}ERROR:${_RESET} ${1}"
    exit 1
  }

  # Displays an info message.
  # @param {string} the info message to display.
  function info_message() {
    [[ -z "${1}" ]] && error_message "info_message requires one argument."
    echo -e "${_GREEN}INFO:${_RESET} ${1}"
  }

  # Displays an success message.
  # @param {string} the success message to display.
  function success_message() {
    [[ -z "${1}" ]] && error_message "success_message requires one argument."
    echo -e "${_GREEN}SUCCESS:${_RESET} ${1}"
  }

  # Sets the platform for the machine this is running on.
  function platform() {
    UNAME="$(uname -s)"
    case "${UNAME}" in
      Linux*) PLATFORM="${_LINUX}";;
      Darwin*) PLATFORM="${_MAC}";;
      *) error_message "This platform is not recognized";;
    esac
  }

  # Checks whether or not a binary is present in PATH.
  # @param {string} the binary to check.
  # @param {string} error message to display.
  function check_binary() {
    [[ -z "${1}" ]] && error_message "check_binary requires a binary to check"
    [[ -z "${2}" ]] && error_message "check_binary requires an error \
message to display during failure"
    command -v "${1}" > /dev/null 2>&1 || \
      error_message "${1} not found on PATH, ${2}"
  }

  # Checks that gcloud is in PATH and at or above the minimum version.
  function check_gcloud() {
    info_message "Checking for gcloud on PATH and version..."
    check_binary "gcloud" "please install the gcloud sdk to continue, more \
info can be found here: https://cloud.google.com/sdk/downloads"
    case "${PLATFORM}" in
      "${_LINUX}")
        GCLOUD_VERSION=$(gcloud version \
          | head -n 1 \
          | cut -d ' ' -f4 \
          | sed 's/\(^0*\|\.\)//g');;
      "${_MAC}")
        GCLOUD_VERSION=$(gcloud version \
          | head -n 1 \
          | cut -d ' ' -f4 \
          | sed -E 's/(^0*|\.)//g');;
    esac
    [[ "${GCLOUD_VERSION}" -ge "18600" ]] || error_message "The gcloud \
version installed is lower than the minimum required version (186.0.0), \
please update gcloud."
    success_message "gcloud was found on PATH and is at or above the minimum \
version."
  }

  # Checks that bazel is in PATH and at or above the minimum version.
  function check_bazel() {
    info_message "Checking for bazel on PATH and version..."
    check_binary "bazel" "please install bazel to continue, more info can be \
found here: https://docs.bazel.build/versions/master/install.html"
    case "${PLATFORM}" in
      "${_LINUX}")
        BAZEL_VERSION=$(bazel version \
          | head -n 1 \
          | cut -d ' ' -f3 \
          | sed 's/\(^0*\|\.\)//g');;
      "${_MAC}")
        BAZEL_VERSION=$(bazel version \
          | head -n 1 \
          | cut -d ' ' -f3 \
          | sed -E 's/(^0*|\.)//g');;
    esac
    [[ "${BAZEL_VERSION}" -ge "90" ]] || error_message "The bazel vesrion \
installed is lower than the minimum required version (0.9.0), please update \
bazel."
    success_message "bazel was found on PATH and is at or above the minimum \
version."
  }

  # Checks that npm is in PATH and at or above the minimum version (5.5.1).
  function check_npm() {
    info_message "Checking for npm on PATH and version..."
    check_binary "npm" "please install npm to continue, more info can be \
found here: https://www.npmjs.com/get-npm"
    case "${PLATFORM}" in
      "${_LINUX}")
        NPM_VERSION=$(npm -v | sed 's/\(^0*\|\.\)//g');;
      "${_MAC}")
        NPM_VERSION=$(npm -v | sed -E 's/(^0*|\.)//g');;
    esac
    [[ "${NPM_VERSION}" -ge "530" ]] || error_message "The npm version \
installed is lower than the minimum version (5.3.0), please update npm."
    success_message "npm was found on PATH and is at or above the minimum \
version."
  }

  # Check that the gcloud SDK has been configured with an authenticated account.
  function check_gcloud_auth() {
    info_message "Checking gcloud authentication..."
    [[ -n $(gcloud info --format="value(config.account)") ]] || error_message \
"gcloud does not have an account configured, please run gcloud init or gcloud \
auth login"
  }

  # Check that the script was executed from within the loaner directory and goto
  # the loaner directory. Also, make sure the bazel BUILD files exist to build
  # deploy_impl.py.
  function goto_loaner_dir() {
    info_message "Going to the loaner directory..."
    # Resolve current directory of the script and any symbolic links
    if [[ "${PLATFORM}" == "${_MAC}" ]]; then
      local pwd=$(pwd -P)
      case "${pwd}" in
        */loaner/loaner)
          ;;
        */loaner/loaner/*)
          cd "${pwd%%/loaner/loaner/*}/loaner/loaner"
          ;;
        */loaner)
          cd "${pwd%%/loaner/*}/loaner"
          ;;
        */loaner/*)
          cd "${pwd%%/loaner/*}/loaner"
          ;;
        *)
          error_message "This script must be run within the loaner directory."
          ;;
      esac
    else
      DEPLOY_PATH="$(dirname "$(readlink -f "${0}")")"
      # cd to the 'loaner/loaner/' directory.
      cd "${DEPLOY_PATH}" && cd ..
    fi


    # Make sure we are in the loaner directory.
    if [[ ${PWD##*/} != "loaner" ]]; then
      error_message "This script must be located in the loaner/deployments \
      directory."
    fi

    # Check for the WORKSPACE file and that the requisite BUILD files exist.
    if [[ ! -f ../WORKSPACE || ! -f BUILD || ! -f deployments/BUILD ]]; then
      error_message "The Bazel BUILD files appear to be missing."
    fi
  }

  # Check that the required binaries are on PATH and above the minimum version.
  if [[ "${BINARY_CHECK}" = true ]]; then
    platform
    check_gcloud
    check_bazel
    check_npm
  else
    info_message "Skipping binary check..."
  fi

  if [[ "${GCLOUD_AUTH_CHECK}" = true ]]; then
    check_gcloud_auth
  else
    info_message "Skipping gcloud auth check..."
  fi

  goto_loaner_dir

  info_message "Initiating the build of the python deployment script..."
  bazel build //loaner/deployments:deploy_impl

  ../bazel-out/k8-py3-fastbuild/bin/loaner/deployments/deploy_impl \
    --loaner_path "$(pwd -P)" \
    --app_servers "${APP_SERVERS}" \
    --build_target "${BUILD_TARGET}" \
    --chrome_app_dir "${CHROME_APP_DIR}" \
    --web_app_dir "${WEB_APP_DIR}" \
    --yaml_files "${SERVICES},${CONFIGS}" \
    "${@}"

fi  # End include guard
