#!/bin/bash
#
# Execute backend bazel tests.
#   Usage: ./backend_tests.sh SHARD_INDEX TOTAL_NUMBER_OF_SHARDS

set -e

CURRENT_TEST_GROUP=${1:-0}
TOTAL_TEST_GROUPS=${2:-1}
ALL_TESTS=$(bazel query 'tests(//loaner/...)')
NUM_TESTS=$(echo "${ALL_TESTS}" | wc -w)

GROUP_SIZE=$(echo "1 + ${NUM_TESTS} / ${TOTAL_TEST_GROUPS}" | bc)
LOWER_BOUND=$(echo "${CURRENT_TEST_GROUP} * ${GROUP_SIZE}" | bc)
UPPER_BOUND=$(echo "${LOWER_BOUND} + ${GROUP_SIZE}" | bc)

CURRENT_TESTS=$(echo "${ALL_TESTS}" | tr "\n" " " | python -c "print ' '.join(raw_input().split()[${LOWER_BOUND}:${UPPER_BOUND}])")
if [[ -n "${CURRENT_TESTS}" ]]; then
  bazel test --curses=no --test_output=errors --spawn_strategy=standalone \
    --test_strategy=standalone --verbose_failures ${CURRENT_TESTS}
fi
