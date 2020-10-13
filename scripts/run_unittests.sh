set -eu
set -o pipefail
set -x

python3 -m unittest discover -v
