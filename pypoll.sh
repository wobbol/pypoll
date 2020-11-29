#!/bin/sh

set -e
DIR=$(dirname $0)
source "$DIR/venv/bin/activate"
export FLASK_APP="$DIR/pypoll.py"
export FLASK_ENV=development
cd "$DIR"
python3 << EOF
import pypoll
f = None
try:
    f = open(pypoll.database)
    f.close()
except IOError:
    with pypoll.app.app_context():
        pypoll.create_tables()
EOF
cd -
flask run

