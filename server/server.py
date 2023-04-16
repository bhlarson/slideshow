#!/usr/bin/python3
# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================
import sys, os, re
import uuid
import time
import yaml
import pickle
import pprint
import random
from os.path import dirname, abspath, join, isdir
from os import listdir
from pathlib import Path
from hmac import compare_digest
from flask import Flask, request, jsonify, send_from_directory, Response, logging
from flask_httpauth import HTTPTokenAuth
from flask_socketio import SocketIO, ConnectionRefusedError, Namespace, emit
import asyncio
import threading
import time
import logging

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
    parser.add_argument('-port', type=int, default=5000, help='webserver port')
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
    parser.add_argument('-pictures', type=str, default='/farm/pictures', help='Pictures path')


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
def get_static():
    return send_from_directory("../ui/", "index.html")

@app.route('/<file>', defaults={'path': ''})
@app.route('/<path:path>/<file>')
def get_files(path, file):
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

# Serch is regex string.  e.g. '(?i)(?!thumb)'. https://regex101.com/, https://docs.python.org/3/library/re.html
def ImageList(path= '/farm/pictures/', extensions = ['.png', '.jpg'], search = r'(?:thumb|trash)', reflags = re.IGNORECASE):
    filelist = []
    # Convert extensions to lower case once at the beginning
    for i, ext in enumerate(extensions):
        extensions[i] = ext.lower()

    for root, dirs, files in os.walk(path):
        for file in files:
            if extensions is not None:
                extmatch = False
                ext = Path(file).suffix.lower()
                for extension in extensions:
                    if(ext == extension):
                        extmatch = True
                        break
            else:
                extmatch = True
            if extmatch:
                if search is not None:
                    match = re.search(search, file, reflags)
                    if not match:
                        filelist.append('{}/{}'.format(root, file))
                else:
                    filelist.append('{}/{}'.format(root, file))

    random.shuffle(filelist)
    return filelist

def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)
   
def main(args):          
    print("Server starting at : http://" + args.client_address + ":" + str(args.port) + "/")

    images = ImageList(args.pictures)

    logging.info("Main    : before creating thread")
    x = threading.Thread(target=thread_function, args=(1,))
    logging.info("Main    : before running thread")
    x.start()
    logging.info("Main    : wait for the thread to finish")
    # x.join()
    logging.info("Main    : all done")

    socketio.run(app, host=args.client_address, port=args.port, debug=False)


if __name__ == '__main__':
    args = parse_arguments()

    if args.debug:
        print("Wait for debugger attach on {}:{}".format(args.debug_address, args.debug_port))
        import debugpy
        debugpy.listen(address=(args.debug_address, args.debug_port)) # Pause the program until a remote debugger is attached
        debugpy.wait_for_client() # Pause the program until a remote debugger is attached
        print("Debugger attached")

    main(args)
