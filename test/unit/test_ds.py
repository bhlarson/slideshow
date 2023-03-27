import os, io, sys, json, datetime
import unittest
from pymlutil.jsonutil import *

sys.path.insert(0, os.path.abspath(''))

test_config = 'test.yaml'
args = ReadDict(test_config)

class Test(unittest.TestCase):
    def test_tables(self):
        global args
        print('OK') 
    


       
if __name__ == '__main__':

    if args['debug']:
        print("Wait for debugger attach on {}:{}"
              .format(args['debug_address'], args['debug_port']))
        import debugpy

        debugpy.listen(address=(args['debug_address'], args['debug_port'])) # Pause the program until a remote debugger is attached
        debugpy.wait_for_client() # Pause the program until a remote debugger is attached
        print("Debugger attached")

    unittest.main()