import unittest
import os, sys
import string
import itertools
import zipfile
import zlib

import test_singlefile

class TestDirectories(test_singlefile.SingleTextFile):
    def setUp(self):
        self.set_names()
        self.make_tmp_dir()
        self.make_directories_tree()
        cmd = ['zip', '-r', self.arch_name, self.sample_name]
        res = self.run_cmd(cmd)
        self.assertEqual(res, 0, msg=f'Exit code is {res}.')

    def make_directories_tree(self):
        symbols = string.ascii_letters
        names = itertools.permutations(symbols, 12)
        os.mkdir(self.sample_name)
        self.files = set()
        self.files.add(self.sample_name + '/')
        # C надеждой, что zip для MacOS хранит пути в posix:  
        for i in range(3):
            for r, d, f in os.walk(self.sample_name):
               dir_name  = os.path.join(r, ''.join(next(names)), '')
               os.makedirs(dir_name)
               if sys.platform.startswith('win'):
                   dir_name = dir_name.replace('\\', '/')
               self.files.add(dir_name)
               for j in range(2):
                   fname = os.path.join(r, ''.join(next(names)))
                   self.make_data(fname)
                   if sys.platform.startswith('win'):
                        fname = fname.replace('\\', '/')
                   self.files.add(dir_name)
                   self.files.add(fname)

    def make_data(self, fname):
        data = string.ascii_letters*10
        with open(fname, 'w') as f:
            f.write(data)

    def test_02_file_in_arch(self):
        with zipfile.ZipFile(self.arch_name, 'r') as z:
            names = set(z.namelist())
            self.assertEqual(self.files, names, msg='No testsample in archive.')

    def test_04_can_unpack(self):
        with zipfile.ZipFile(self.arch_name, 'r') as z:
            z.extractall(path=self.unpack_dir)
        self.assertTrue(os.path.exists(self.unpacked_file), msg='Testsample was not created.')

    def test_05_crc32(self):
        files  = [f for f in self.files if f.endswith('/')==False]
        sample = files[3]
        with zipfile.ZipFile(self.arch_name, 'r') as z:
            z.extract(sample, path=self.unpack_dir)
            info = z.getinfo(sample)
            src_crc = info.CRC
        with open(sample, 'r') as f:
            data = f.read()
        unpacked_crc = zlib.crc32(data.encode())
        self.assertEqual(src_crc, unpacked_crc)    
        
    def test_06_was_compressed(self):
        self.skipTest('Already tested.(?)')


if __name__ == '__main__':
    unittest.main()
