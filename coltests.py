import os
import shutil
import unittest
import builders
from cols import run

class TestRendering(unittest.TestCase):
    def test_nochange(self):
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           \n"
            "   - 2 - 2\n"
            "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n",False)
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'),"file exists")

def setup_testing():
    print('Setting up...')
    if os.path.exists('cols'):
        shutil.rmtree('cols',ignore_errors=True)
    if os.path.isfile('locs.json'):
        os.remove('locs.json')
    run("---\n"
        "- a - anime\n"
        "   - 1 - 1\n"
        "       - a\n"
        "           \n"
        "   - 2 - 2\n"
        "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n")
    print('[READY]')

if __name__=='__main__':
    setup_testing()
    unittest.main()