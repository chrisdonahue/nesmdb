from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext

import os
import shutil
import subprocess
import tarfile
import urllib


_dummy_extension = Extension('vgmplaydummy', sources=[])


class BuildVGMPlay(build_ext, object):
  def build_extension(self, ext):
    super(BuildVGMPlay, self).build_extension(ext)

    # Get temp dir
    build_temp = self.build_temp
    if not os.path.isdir(build_temp):
      os.makedirs(build_temp)

    # Download VGMPlay 0.40.8
    print 'Downloading VGMPlay'
    tgz_filepath = os.path.join(self.build_temp, '0.40.8.tar.gz')
    urllib.urlretrieve(
        'https://github.com/vgmrips/vgmplay/archive/0.40.8.tar.gz',
        tgz_filepath)

    # Extract
    print 'Extracting VGMPlay'
    with tarfile.open(tgz_filepath, 'r:gz') as f:
      f.extractall(build_temp)
    vgmplay_dir = os.path.join(build_temp, 'vgmplay-0.40.8', 'VGMPlay')
    if not os.path.isdir(vgmplay_dir):
      raise Exception('Could not extract VGMPlay')

    # Build
    print 'Building VGMPlay'
    command = 'make -C {} vgm2wav'.format(vgmplay_dir)
    res = subprocess.call(command.split())
    if res > 0:
      raise Exception('Error building VGMPlay')

    # Get build dir
    import imp
    build_lib = os.path.dirname(imp.find_module('vgmplaydummy')[1])

    # Copy binary to build dir
    bin_fp = os.path.join(vgmplay_dir, 'vgm2wav')
    if not os.path.isfile(bin_fp):
      raise Exception('Could not find binary')
    shutil.copy(bin_fp, build_lib)

    # Cleanup
    os.remove(tgz_filepath)
    shutil.rmtree(os.path.join(build_temp, 'vgmplay-0.40.8'))


setup(
    name='nesmdb',
    version='0.1.3',
    description='The NES Music Database (NES-MDB). Use machine learning to compose music for the Nintendo Entertainment System!',
    author='Chris Donahue',
    author_email='cdonahue@ucsd.edu',
    url='https://github.com/chrisdonahue/nesmdb',
    download_url='https://github.com/chrisdonahue/nesmdb/releases',
    license='MIT',
    packages=['nesmdb', 'nesmdb.vgm', 'nesmdb.score'],
    keywords='music nes mir midi',
    python_requires='>=2.7,<3.0',
    install_requires=[
      'numpy >= 1.7.0',
      'scipy >= 1.0.0',
      'Pillow >= 5.1.0',
      'tqdm >= 4.19.9',
    ],
    test_suite='nose.collector',
    tests_require=[
      'nose >= 1.3.7',
      'pretty_midi >= 0.2.8',
      'librosa >= 0.6.1',
    ],
    cmdclass = {'build_ext': BuildVGMPlay},
    ext_modules = [_dummy_extension],
)
