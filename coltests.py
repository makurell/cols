import os
import shutil
import unittest
import builders
from cols import internal_run

TEST_EXTENT = 0


class TestRendering(unittest.TestCase):
    def test_a_nochange(self):
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "file exists")

    def test_b_move(self):
        # move
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "dest file exists")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "src file removed")
        # move back
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "dest file exists")
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "src file removed")

    def test_c_copy(self):
        # copy
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "dest file exists")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "src file exists")
        # delete top
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file exists")
        # copy again
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "dest file exists")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "src file exists")
        # delete bottom
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file exists")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # move top to bottom (reset)
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file exists")

    def test_d_delete(self):
        # delete
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # create new at top
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file exists")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # delete
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # create two copies at once
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertTrue(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file exists")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file exists")
        # delete both
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file removed")
        # create new at bottom (reset)
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file removed")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file exists")

    def test_e_redownload(self):
        os.remove('cols/a/2/moe.jpeg')
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file does not exist")
        self.assertTrue(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file exists")

    def test_f_reset(self):
        if TEST_EXTENT < 2: return
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isfile('cols/a/1/a/moe.jpeg'), "top file does not exist")
        self.assertFalse(os.path.isfile('cols/a/2/moe.jpeg'), "bottom file does not exist")

    def test_g_m(self):
        if TEST_EXTENT < 2: return
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n", False)
        self.assertTrue(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")

    def test_h_m_nochange(self):
        if TEST_EXTENT < 2: return
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n", False)
        self.assertTrue(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")

    def test_i_m_move(self):
        if TEST_EXTENT < 2: return
        # move up
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertTrue(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # and back
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n", False)
        self.assertTrue(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertFalse(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")

    def test_j_m_copy(self):
        if TEST_EXTENT < 2: return
        # copy
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n"
                     "   - 2 - 2\n"
                     "       https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n", False)
        self.assertTrue(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertTrue(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # delete top
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n", False)
        self.assertTrue(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertFalse(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # copy again
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n"
                     "   - 2 - 2\n"
                     "       https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n", False)
        self.assertTrue(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertTrue(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # delete bottom
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertTrue(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # move to bottom (reset)
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n", False)
        self.assertTrue(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertFalse(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")

    def test_k_m_delete(self):
        if TEST_EXTENT < 3: return
        # delete
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertFalse(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # create new copy at top
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertTrue(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # delete
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertFalse(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # create 2 new copies at once
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n"
                     "   - 2 - 2\n"
                     "       https://www.pixiv.net/member_illust.php?mode=medium&illust_id=68427137\n", False)
        self.assertTrue(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertTrue(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertTrue(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertTrue(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")
        # delete both
        internal_run("---\n"
                     "- a - anime\n"
                     "   - 1 - 1\n"
                     "       - a\n"
                     "           \n"
                     "   - 2 - 2\n"
                     "       \n", False)
        self.assertFalse(os.path.isdir('cols/a/2/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p0.jpg'), "bottom0")
        self.assertFalse(os.path.isfile('cols/a/2/Lpip_6996493/★_6842713768427137_p1.jpg'), "bottom1")
        self.assertFalse(os.path.isdir('cols/a/1/a/Lpip_6996493/'), 'dir')
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p0.jpg'), "top0")
        self.assertFalse(os.path.isfile('cols/a/1/a/Lpip_6996493/★_6842713768427137_p1.jpg'), "top1")


def setup_testing():
    # print('Setting up...')
    if os.path.exists('cols'):
        shutil.rmtree('cols', ignore_errors=True)
    if os.path.isfile('locs.json'):
        os.remove('locs.json')
    internal_run("---\n"
                 "- a - anime\n"
                 "   - 1 - 1\n"
                 "       - a\n"
                 "           \n"
                 "   - 2 - 2\n"
                 "       https://upload.wikimedia.org/wikipedia/commons/4/43/Chara04.png moe\n", False)
    # print('[READY]')


if __name__ == '__main__':
    TEST_EXTENT = 3
    import cols

    builders.pixiv_username = os.getenv('PIXIV_USERNAME')
    builders.pixiv_password = os.getenv('PIXIV_PASS')

    cols.VERBOSITY = 0
    setup_testing()

    unittest.main(verbosity=2)
