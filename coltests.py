import os
import shutil
import unittest
import builders
from cols import run

class TestRendering(unittest.TestCase):
    def test_nochange(self):
        pass

def setup_testing():
    print('Setting up...')
    if os.path.exists('cols'):
        shutil.rmtree('cols')
    if os.path.isfile('locs.json'):
        os.remove('locs.json')
    run()
    print('[READY]')

if __name__=='__main__':
    setup_testing()
    unittest.main()