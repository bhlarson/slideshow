# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from __future__ import division
import sys, os
import uuid
import time
import yaml
import pickle
import pprint
from os.path import dirname, abspath, join, isdir
from os import listdir
from hmac import compare_digest
from flask import Flask, request, jsonify, send_from_directory, Response, logging
from flask_httpauth import HTTPTokenAuth
from flask_socketio import SocketIO, ConnectionRefusedError, Namespace, emit

ks_key = None
ds = None
tokens = None

global args

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='{} {} parse argument'.format(__file__, __name__))

    parser.add_argument('-d', action='store_true',help='Wait for debuggee attach')   
    parser.add_argument('-debug', type=bool, default=False, help='Wait for debuggee attach')
    parser.add_argument('-debug_port', type=int, default=3000, help='Debug port')
    parser.add_argument('-debug_address', type=str, default='0.0.0.0', help='Debug port')
    parser.add_argument('-min', action='store_true', help='Load minimal data for development')
    parser.add_argument('-creds', type=str, default='creds.yaml', help='Credentials file')
    parser.add_argument('-cert', type=str, default='cert.pem', help='Certificate path')
    parser.add_argument('-key', type=str, default='privkey.pem', help='Key path')
    parser.add_argument('-port', type=int, default=443, help='webserver port')
    parser.add_argument('-client_address', type=str, default='0.0.0.0', help='Client address.  0.0.0.0 accepts all clients')
    parser.add_argument('-verbose', type=bool, default=True, help='Wait for debuggee attach')
    parser.add_argument('-model_dockembedding', type=str, default='text-embedding-ada-002', help='OpenAI model name')
    parser.add_argument('-model_queryembedding', type=str, default='text-embedding-ada-002', help='OpenAI model name')
    parser.add_argument('-completions_engine', type=str, default='text-davinci-003', help='OpenAI model name')
    parser.add_argument('-script', type=str, default='script/full.yaml', help='Embedding match script')
    parser.add_argument('-embeddings', type=str, default='script/full_embeddings.bin', help='Embedding match script')
    parser.add_argument('-real_response_level', type=float, default=0.31, help='Minimum match for a real response')
    parser.add_argument('-api_name', type=str, default='ks', help='API name for application key')
    parser.add_argument('-s3_name', type=str, default='knowledgescope', help='S3 name in credentials')
    parser.add_argument('-api', type=str, default='AzureOpenaiDev', help='Credentials file')
    parser.add_argument('-db', type=str, default='ks', help='Web server port')


    args = parser.parse_args()

    if args.d:
        args.debug = args.d

    return args


''' Flask Initialization 
'''

app = Flask(__name__)
socketio = SocketIO(app)
auth = HTTPTokenAuth(scheme='Bearer')
log = logging.logging.getLogger('werkzeug')
log.setLevel(logging.logging.ERROR)

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

# Methods to show client
@app.route('/')
#@auth.login_required
def get_bot1():
    return send_from_directory("../ui/", "index.html")

@app.route('/<file>', defaults={'path': ''})
@app.route('/<path:path>/<file>')
#@auth.login_required
def get_bot2(path, file):
    return send_from_directory("../ui/" + path, file)

def is_valid(api_key):

    if compare_digest(ks_key, api_key):
        return True

@app.route('/ask', methods=["GET", "PUT"])
def Ask():
    global devices
    result = {}
    request_data = request.json

    if 'question' in request_data:
        print('/ask question: {} '.format(request_data['question']))

    return jsonify(result)


@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print('received json: ' + str(json))

def ack():
    print('message was received!')

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json, namespace='/chat')

@socketio.on('my event')
def handle_my_custom_event(data):
    emit('my response', data, broadcast=True)

@socketio.on('connect')
def connect(auth):
    if not self.authenticate(request.args):
        raise ConnectionRefusedError('unauthorized!')
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    pass

@socketio.on_error('/chat') # handles the '/chat' namespace
def error_handler_chat(e):
    pass

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass

class MyCustomNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_my_event(self, data):
        emit('my_response', data)

socketio.on_namespace(MyCustomNamespace('/test'))

    
def main(args):          

    ssl_context = (args.cert, args.key)
    print("Server starting at : https://" + args.client_address + ":" + str(args.port) + "/")
    socketio.run(app, host=args.client_address, port=args.port, debug=False, ssl_context=ssl_context)


if __name__ == '__main__':
    args = parse_arguments()

    if args.debug:
        print("Wait for debugger attach on {}:{}".format(args.debug_address, args.debug_port))
        import debugpy
        debugpy.listen(address=(args.debug_address, args.debug_port)) # Pause the program until a remote debugger is attached
        debugpy.wait_for_client() # Pause the program until a remote debugger is attached
        print("Debugger attached")

    main(args)
