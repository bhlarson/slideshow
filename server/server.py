# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import sys, os, re, json, yaml
from os.path import dirname, abspath, join, isdir
from os import listdir
import random
from pathlib import Path
from flask import request
from flask import Flask, jsonify, send_from_directory, Response, logging
from flask_socketio import SocketIO, emit
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
    parser.add_argument('-client_address', type=str, default='0.0.0.0', help='Client address.  0.0.0.0 accepts all clients')
    parser.add_argument('-port', type=int, default=80, help='webserver port')
    parser.add_argument('-credentials', type=str, default='creds.yaml', help='Credentials path')
    parser.add_argument('-apikey', type=str, default='slideshow', help='Credentials path')


    args = parser.parse_args()

    if args.d:
        args.debug = args.d

    return args

def ReadDictJson(filepath):
    jsondict = None
    try:
        with open(filepath) as json_file:
            jsondict = json.load(json_file)
        if not jsondict:
            print('Failed to load {}'.format(filepath))
    except Exception as err:
        print("Exception {}: ReadDictJson failed to load {}.  {}".format(type(err), filepath, err))
        raise err
    return jsondict

def ReadDictYaml(filepath):
    yamldict = {}
    try:
        with open(filepath) as yaml_file:
            yamldict = yaml.safe_load(yaml_file)
        if not yamldict:
            print('Failed to load {}'.format(filepath))
    except Exception as err:
        print("Exception {}: ReadDictYaml failed to load {}.  {}".format(type(err), filepath, err))
        raise err
    return yamldict

def ReadDict(filepath):
    if filepath[0] == '~':
        filepath = os.path.expanduser(filepath)
    ext = os.path.splitext(filepath)[1]
    if ext=='.yaml':
        readDict = ReadDictYaml(filepath)
    elif ext=='.json':
        readDict = ReadDictJson(filepath)
    else:
        readDict = None
    return readDict


''' Flask Initialization 
'''
send = True
args = parse_arguments()
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
creds = ReadDict(args.credentials)
client_key = next(filter(lambda d: d.get('name') == args.apikey, creds['api']), None)
assert client_key is not None

app.config['SECRET_KEY'] = client_key['key']
socketio = SocketIO(app)

# Methods to show client
@app.route('/')
def get_static():
    return send_from_directory("../ui/", "index.html")

@app.route('/<file>', defaults={'path': ''})
@app.route('/<path:path>/<file>')
def get_files(path, file):
    return send_from_directory("../ui/" + path, file)

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

@socketio.on('my_event')
def handle_my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)

@socketio.event
def my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)

@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print('received json: ' + str(json))

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

def thread_function():
    images = ImageList()
    app.logger.info("Thread starting")
    while send:

        emit('my response', {'message': 'Hello'} )
        app.logger.info("emit")
        time.sleep(2)
    
def main(args):

    # app.logger.info("Main    : before creating thread")
    # # x = threading.Thread(target=thread_function, args=(1,))
    # app.logger.info("Main    : before running thread")
    # x.start()
    thread = socketio.start_background_task(target=thread_function)


    print("Server starting at : https://" + args.client_address + ":" + str(args.port) + "/")
    socketio.run(app, host=args.client_address, port=args.port, debug=False)


    app.logger.info("Main    : wait for the thread to finish")
    send = False
    thread.join()
    app.logger.info("Main    : all done")

if __name__ == '__main__':

    if args.debug:
        print("Wait for debugger attach on {}:{}".format(args.debug_address, args.debug_port))
        import debugpy
        debugpy.listen(address=(args.debug_address, args.debug_port)) # Pause the program until a remote debugger is attached
        debugpy.wait_for_client() # Pause the program until a remote debugger is attached
        print("Debugger attached")

    main(args)
