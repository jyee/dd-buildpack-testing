# Flask
from flask import Flask, request
import os
import random
import time

# Datadog tracing and metrics
import blinker as _
from datadog import statsd
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

env = os.environ.get('DD_SERVICE_ENV')

# Index page.
@app.route('/')
def index():
    tags = ['env: {}'.format(env), 'page:index']
    statsd.increment('buildpack_testing.views', tags=tags)
    time.sleep(random.randint(0,5))
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
