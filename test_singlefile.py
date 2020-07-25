import unittest
import os, sys
import string
import subprocess
import zipfile
import hashlib
import shutil

class SingleTextFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cmd = cls.make_cmd('-h')
        try:
            cls.run_cmd(cmd)
        except FileNotFoundError:
            print('Zip executable not found.')
            sys.exit(1)

    @classmethod
    def make_cmd(cls, flags, arc='', sample=''):
        if sys.platform.startswith('win'):
            exe = 'zip.exe'
        else:
            exe = 'zip'
        res = f'{exe} {flags} {arc} {sample}'.split()
        return res

    @classmethod
    def run_cmd(cls, cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _, _ = proc.communicate()
        return proc.returncode

    def setUp(self):
        self.test_dir = 'test_dir'
        self.unpack_dir = os.path.join(self.test_dir, 'unpack')
        self.unpacked_file = os.path.join(self.unpack_dir, 'testsample')

        os.makedirs(self.unpack_dir)
        os.chdir(self.test_dir)

        self.data = string.ascii_letters*10
        with open('testsample', 'w') as f:
            f.write(self.data)

        cmd = self.make_cmd('', 'testsample.zip', 'testsample')
        res = self.run_cmd(cmd)
        self.assertEqual(res, 0, msg=f'Exit code is {res}.')

    def tearDown(self):
        os.chdir('..')
        shutil.rmtree(self.test_dir)

    def test_01_zip_file_exists(self):
        self.assertTrue(os.path.exists('testsample.zip'), msg='testsample.zip was not created.')

    def test_02_file_in_arch(self):
        with zipfile.ZipFile('testsample.zip', 'r') as z:
            names = z.namelist()
            self.assertEqual('testsample', names[0], msg='No testsample in archive.')

    def test_03_zipfile(self):
        with zipfile.ZipFile('testsample.zip', 'r') as z:
           res = z.testzip()
        self.assertIsNone(res, msg='testsample.zip is corrupted.')
 
    def test_04_can_unpack(self):
        with zipfile.ZipFile('testsample.zip', 'r') as z:
            z.extract('testsample', path=self.unpack_dir)
        self.assertTrue(os.path.exists(self.unpacked_file), msg='testsample was not created.')

    def test_05_md5(self):
        with zipfile.ZipFile('testsample.zip', 'r') as z:
            z.extract('testsample', path=self.unpack_dir)
        md5_src = hashlib.md5(self.data.encode())
        md5_src = md5_src.hexdigest()
        with open(self.unpacked_file, 'r') as f:
            data = f.read()
        md5_unpack = hashlib.md5(data.encode())
        md5_unpack = md5_unpack.hexdigest()
        self.assertEqual(md5_unpack, md5_src)

    def test_06_was_compressed(self):
        with zipfile.ZipFile('testsample.zip', 'r') as z:
            info = z.infolist()[0]
            diff = info.file_size - info.compress_size
        self.assertGreater(diff, 0, msg='The sample was not compressed.')

    def test_07_can_not_unpack_wrong_file(self):
        with zipfile.ZipFile('testsample.zip', 'r') as z:
            with self.assertRaises(KeyError) as _:
                z.extract('wrong_sample_test')

    def test_08_wrong_sample_not_exists(self):
        self.assertFalse(os.path.exists('wrong_sample_test'))

if __name__ == '__main__':
    unittest.main()
