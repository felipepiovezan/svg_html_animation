set -eu
set -o pipefail
set -x

# Use this script to know if the PR check will fail.
autopep8 --diff --aggressive --aggressive --exit-code --recursive .
