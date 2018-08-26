import os
import shutil
import unittest
import builders
from cols import run

class TestRendering(unittest.TestCase):
    def test_1_nochange(self):
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           \n"
            "   - 2 - 2\n"
            "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n",False)
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'),"file exists")

    def test_2_move(self):
        # move
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
            "   - 2 - 2\n"
            "       \n",False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'),"dest file exists")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'),"src file removed")
        # move back
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           \n"
            "   - 2 - 2\n"
            "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "dest file exists")
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "src file removed")

    def test_3_copy(self):
        # copy
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
            "   - 2 - 2\n"
            "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "dest file exists")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "src file exists")
        # delete top
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           \n"
            "   - 2 - 2\n"
            "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file exists")
        # copy again
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
            "   - 2 - 2\n"
            "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "dest file exists")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "src file exists")
        # delete bottom
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
            "   - 2 - 2\n"
            "       \n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file exists")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # move top to bottom (reset)
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           \n"
            "   - 2 - 2\n"
            "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file exists")

    def test_4_delete(self):
        # delete
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           \n"
            "   - 2 - 2\n"
            "       \n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # create new at top
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
            "   - 2 - 2\n"
            "       \n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file exists")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # delete
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           \n"
            "   - 2 - 2\n"
            "       \n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # create two copies at once
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
            "   - 2 - 2\n"
            "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file exists")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file exists")
        # delete both
        run("---\n"
            "- a - anime\n"
            "   - 1 - 1\n"
            "       - a\n"
            "           \n"
            "   - 2 - 2\n"
            "       \n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")

        #todo implement when actual image file deleted externally, redownload

def setup_testing():
    # print('Setting up...')
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
        "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n",False)
    # print('[READY]')

if __name__=='__main__':
    import cols
    cols.DEBUG = False
    setup_testing()

    unittest.main(verbosity=2)