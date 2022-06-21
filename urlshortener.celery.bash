NAME="urlshortener_celery"
DJANGODIR=/webapps/urlshortener
DJANGO_SETTINGS_MODULE=urlshortener.settings
DJANGO_WSGI_MODULE=urlshortener.wsgi

echo "Starting $NAME as `whoami`"

cd $DJANGODIR
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

exec celery -A urlshortener worker -l debug -n urlshortener@%h -E -B