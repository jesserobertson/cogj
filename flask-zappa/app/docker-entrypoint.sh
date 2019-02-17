#!/bin/sh

CMD="$1"

if [ "$ENVIRONMENT" = "DEVELOPMENT" ]; then
  flask run --host=0.0.0.0 --port=$FLASK_PORT
fi

if [ "$CMD" = "uwsgi" ]; then
   export ENVIRONMENT=PRODUCTION
   chown 1000:1000 /var/log/uwsgi/uwsgi.log
   uwsgi --lazy-apps --uid 1000 --gid 1000 --http-socket 0.0.0.0:5000 --manage-script-name --chdir /home/geolambda/work/api --mount /=app:app --master --processes 3 --threads 3 --logto /var/log/uwsgi/uwsgi.log --harakiri 120
   exit
fi