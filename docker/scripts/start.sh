

mv docker/nginx/default /etc/nginx/sites-enabled/default

echo "Testing NGINX configuration"
nginx -t

echo "Starting NGINX service"
service nginx start

source venv/bin/activate
NUM_CORES=$( getconf _NPROCESSORS_ONLN )
echo "$NUM_CORES cpu cores detected on system"

if [ "$FLASK_ENV" == "development" ]
then
    echo "Starting application in development mode"
    python app.py
else
    echo "Generating initial data csv"
    python app.py -g
    echo "Starting application with $NUM_CORES workers"
    gunicorn -w $NUM_CORES app:server -b 127.0.0.1:8050 -t 600
fi