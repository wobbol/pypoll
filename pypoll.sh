#!/bin/sh

set -e
DIR=$(dirname $0)
source "$DIR/venv/bin/activate"
export FLASK_APP="$DIR/pypoll.py"
export FLASK_ENV=development
cd "$DIR"
python3 << EOF
import pypoll
f = {}
try:
    f = open(pypoll.database)
except IOError:
    with pypoll.app.app_context():
        pypoll.create_tables()
finally:
    f.close()
EOF
cd -
flask run

