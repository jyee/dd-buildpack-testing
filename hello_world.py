# Flask
from flask import Flask, request
import os

# Datadog tracing and metrics
import blinker as _
from datadog import initialize, api, statsd
from ddtrace import tracer
from ddtrace.contrib.flask import TraceMiddleware

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

traced_app = TraceMiddleware(app, tracer, service=os.environ.get('DD_SERVICE_NAME'))

debug = os.environ.get('DEBUG', False)
if os.environ.get('DD_SERVICE_ENV') != 'production':
    debug = True

# Setup additional logging when not on prod.
if debug:
    import logging
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

# Initialize Datadog
options = {
    'api_key': os.environ.get('DD_API_KEY'),
    'app_key': os.environ.get('DD_APP_KEY')
}
initialize(**options)


# Index page.
@app.route('/')
def index():
    tags = ['env:' + os.environ.get('DD_SERVICE_ENV'), 'page:index']
    statsd.increment('studentpack.page.views', tags=tags)

    return "OHAI World!"


# Define error pages
@app.errorhandler(404)
def page_not_found(e):
	return "That's not a thing here.", 404


@app.errorhandler(500)
def shit_happened(e):
    return "Something went very wrong. :(", 500


if __name__ == '__main__':
    app.run(debug=debug)
