#!/bin/bash

NAME="urlshortener"
DJANGODIR=/webapps/urlshortener
SOCKFILE=$DJANGODIR/run/gunicorn.sock
USER=urlurlurlshortener
GROUP=webapps
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=urlshortener.settings
DJANGO_WSGI_MODULE=urlshortener.wsgi

echo "Starting $NAME as `whoami`"

cd $DJANGODIR
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-