#!/bin/sh

set -e
DIR=$(dirname $0)
source "$DIR/venv/bin/activate"
export FLASK_APP="$DIR/pypoll.py"
export FLASK_ENV=development
flask run

