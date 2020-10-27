set -eu
set -o pipefail
set -x

PYTHONPATH=. python3 examples/example.py examples/example.svg temp.html
