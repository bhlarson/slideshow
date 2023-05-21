# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import sys, os, re
from os.path import dirname, abspath, join, isdir
from os import listdir
import random
from pathlib import Path
from flask import request
from flask import Flask, jsonify, send_from_directory, Response, logging
import threading
import time

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


    args = parser.parse_args()

    if args.d:
        args.debug = args.d

    return args


''' Flask Initialization 
'''

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)

# Methods to show client
@app.route('/')
def get_static():
    return send_from_directory("../ui/", "index.html")

@app.route('/<file>', defaults={'path': ''})
@app.route('/<path:path>/<file>')
def get_files(path, file):
    return send_from_directory("../ui/" + path, file)

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
    images = ImageList()
    log.info("Thread %s: starting", name)
    time.sleep(2)
    log.info("Thread %s: finishing", name)
    
def main(args):

    log.info("Main    : before creating thread")
    x = threading.Thread(target=thread_function, args=(1,))
    log.info("Main    : before running thread")
    x.start()

    print("Server starting at : https://" + args.client_address + ":" + str(args.port) + "/")
    app.run (host=args.client_address, port=args.port, debug=False)

    log.info("Main    : wait for the thread to finish")
    # x.join()
    log.info("Main    : all done")

if __name__ == '__main__':
    args = parse_arguments()

    if args.debug:
        print("Wait for debugger attach on {}:{}".format(args.debug_address, args.debug_port))
        import debugpy
        debugpy.listen(address=(args.debug_address, args.debug_port)) # Pause the program until a remote debugger is attached
        debugpy.wait_for_client() # Pause the program until a remote debugger is attached
        print("Debugger attached")

    main(args)
