# PyPoll

Something close enough to google forms to be useful.

## Dependancies

- sqlite3
- python3
- flask

## Run

```sh
      $ virtualenv3 venv
      $ source venv/bin/activate
(venv)$ pip install -r requirements.txt
(venv)$ deactivate
      $ pypoll.sh
```
Then visit http://127.0.0.1:5000


## Goals

- gather data
  - user
    - multiple choice
    - freeform
  - server
    - /health
      - git commit hash
      - server load
    - /metrics
      - prometheus endpoint
      - json
- data export
  - csv
  - sqlite3
- Initializes its own database

## Anti-goals

- js
- code required for users
- themes
- charts
