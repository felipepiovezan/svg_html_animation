set -eu
set -o pipefail
set -x

python -m unittest discover
