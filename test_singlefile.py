import unittest
import os, sys
import string
import subprocess
import zipfile
import hashlib
import shutil
import zlib

class SingleTextFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cmd = ['zip', '-h']
        try:
            cls.run_cmd(cmd)
        except FileNotFoundError:
            print('Zip executable not found.')
            sys.exit(1)

    @classmethod
    def run_cmd(cls, cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _, _ = proc.communicate()
        return proc.returncode

    def setUp(self):
        self.set_names()
        self.make_tmp_dir()
        self.make_data()
        cmd = ['zip', self.arch_name, self.sample_name]
        res = self.run_cmd(cmd)
        self.assertEqual(res, 0, msg=f'Exit code is {res}.')

    def make_tmp_dir(self):
        self.test_dir = 'test_dir'
        self.unpack_dir = os.path.join(self.test_dir, 'unpack')
        self.unpacked_file = os.path.join(self.unpack_dir, self.sample_name)
        os.makedirs(self.unpack_dir)
        os.chdir(self.test_dir)

    def make_data(self):
        self.data = string.ascii_letters*10
        with open(self.sample_name, 'w') as f:
            f.write(self.data)

    def set_names(self):
        self.arch_name ='testsample.zip'
        self.sample_name = self.zip_sample_name ='TestSample'

    def tearDown(self):
        os.chdir('..')
        shutil.rmtree(self.test_dir)

    def test_01_zip_file_exists(self):
        self.assertTrue(os.path.exists(self.arch_name), msg='Archive was not created.')

    def test_02_file_in_arch(self):
        with zipfile.ZipFile(self.arch_name, 'r') as z:
            names = z.namelist()
            self.assertEqual(self.zip_sample_name, names[0], msg='No testsample in archive.')

    def test_03_zipfile(self):
        with zipfile.ZipFile(self.arch_name, 'r') as z:
           res = z.testzip()
        self.assertIsNone(res, msg='Archive is corrupted.')
 
    def test_04_can_unpack(self):
        with zipfile.ZipFile(self.arch_name, 'r') as z:
            z.extract(self.zip_sample_name, path=self.unpack_dir)
        self.assertTrue(os.path.exists(self.unpacked_file), msg='Testsample was not created.')

    def test_05_crc32(self):
        with zipfile.ZipFile(self.arch_name, 'r') as z:
            z.extract(self.zip_sample_name, path=self.unpack_dir)
            info = z.getinfo(self.zip_sample_name)
            src_crc = info.CRC
        with open(self.unpacked_file, 'r') as f:
            data = f.read()
        unpacked_crc = zlib.crc32(data.encode())
        self.assertEqual(src_crc, unpacked_crc)

    def test_06_was_compressed(self):
        with zipfile.ZipFile(self.arch_name, 'r') as z:
            info = z.infolist()[0]
            diff = info.file_size - info.compress_size
        self.assertGreater(diff, 0, msg='The sample was not compressed.')

    def test_07_can_not_unpack_wrong_file(self):
        with zipfile.ZipFile(self.arch_name, 'r') as z:
            with self.assertRaises(KeyError) as _:
                z.extract('wrong_sample_test')
        self.assertFalse(os.path.exists('wrong_sample_test'))


class SingleTextFileUTF8name(SingleTextFile):
    ''' Вероятно для распаковки следовало использовать какой-нибудь unzip.
        Как оказалось, zip для windows, сохраняет имена файлов в "исторической кодировке",
        Относительно кодировки в MacOS информации не нашел.
    '''
    def set_names(self):
        self.arch_name ='Имя_архива.zip'
        self.sample_name ='Имя_файла'
        if sys.platform.startswith('win'):
            self.zip_sample_name = self.sample_name.encode('cp866').decode('cp437')
        else:
            self.zip_sample_name = self.sample_name

    def make_tmp_dir(self):
        self.test_dir = 'test_dir'
        self.unpack_dir = os.path.join(self.test_dir, 'unpack')
        if sys.platform.startswith('win'):
            self.unpacked_file = os.path.join(self.unpack_dir, self.sample_name).encode('cp866').decode('cp437')
        else:
            self.unpacked_file = os.path.join(self.unpack_dir, self.sample_name)
        os.makedirs(self.unpack_dir)
        os.chdir(self.test_dir)

    def test_06_was_compressed(self):
        self.skipTest('Already tested.(?)')

    def test_07_can_not_unpack_wrong_file(self):
        self.skipTest('Already tested.(?)')


if __name__ == '__main__':
    unittest.main()
