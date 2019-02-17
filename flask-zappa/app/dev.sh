#!/bin/bash

export $(xargs < ../secrets/flask.dev.env)

source venv/bin/activate
flask run --host=0.0.0.0 --port=$FLASK_PORT