from __future__ import print_function
import argparse
import os
from wsgiref import simple_server

from jumpgate import wsgi


def main():
    description = 'Start a single-threaded instance of jumpgate.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--config',
                        default=os.environ.get('JUMPGATE_CONFIG'),
                        help='Jumpgate config location')
    parser.add_argument('--host',
                        default='127.0.0.1',
                        help='host to listen on')
    parser.add_argument('--port',
                        type=int,
                        default=5000,
                        help='port to listen on')

    args = parser.parse_args()
    httpd = simple_server.make_server(args.host,
                                      args.port,
                                      wsgi.make_api(args.config))
    print("Starting server on (%s:%s)" % (args.host, args.port))
    print("""
Warning: This is currently a test server for Jumpgate and not fit for
production since it is single-threaded. Use the WSGI application directly
along with a better wsgi server like gunicorn or uwsgi:
    jumpgate.wsgi:make_api()""")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Exiting...")
