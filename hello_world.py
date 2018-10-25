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

# Setup Flask
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
servicename = os.environ.get('DD_SERVICE_NAME')
env = os.environ.get('DD_SERVICE_ENV')

traced_app = TraceMiddleware(app, tracer, service=servicename)

# Setup additional logging.
import logging
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)


# Index page.
@app.route('/')
def index():
    tags = ['env: {}'.format(env), 'page:index']
    statsd.increment('webapp.pageviews', tags=tags)
    time.sleep(random.random())
    do1()
    time.sleep(random.random())
    return "OHAI World!"

@tracer.wrap(service=servicename)
def do1():
    print "doing 1"
    time.sleep(random.random())
    do2()
    time.sleep(random.random())
    do3()
    time.sleep(random.random())
    return True

@tracer.wrap(service=servicename)
def do2():
    print "doing 2"
    time.sleep(random.random())
    if (random.randint(0,10) > 7):
        do3()
    time.sleep(random.random())
    return True

@tracer.wrap(service=servicename)
def do3():
    print "doing 3"
    time.sleep(random.random())
    if (random.randint(0,10) > 9):
        do2()
    time.sleep(random.random())
    return True

# Define error pages
@app.errorhandler(404)
def page_not_found(e):
	return "That's not a thing here.", 404


@app.errorhandler(500)
def shit_happened(e):
    return "Something went very wrong. :(", 500


if __name__ == '__main__':
    app.run(debug=True)
