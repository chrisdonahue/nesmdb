from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

import os
import shutil
import subprocess
import tarfile
import urllib


def _build_vgm_play(build_temp, build_lib):
  # Get temp dir
  made_build_temp = False
  if not os.path.isdir(build_temp):
    os.makedirs(build_temp)
    made_build_temp = True

  # Download VGMPlay 0.40.8
  print 'Downloading VGMPlay'
  tgz_filepath = os.path.join(build_temp, '0.40.8.tar.gz')
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

  # Modify makefile
  makefile_fp = os.path.join(vgmplay_dir, 'Makefile')
  with open(makefile_fp, 'r') as f:
    makefile = f.read()
  makefile = makefile.replace('USE_LIBAO = 1', '#USE_LIBAO = 1')
  with open(makefile_fp, 'w') as f:
    f.write(makefile)

  # Build
  print 'Building VGMPlay'
  command = 'make -C {} vgm2wav'.format(vgmplay_dir)
  res = subprocess.call(command.split())
  if res > 0:
    raise Exception('Error building VGMPlay')

  # Copy binary to build dir
  bin_fp = os.path.join(vgmplay_dir, 'vgm2wav')
  if not os.path.isfile(bin_fp):
    raise Exception('Could not find binary')
  shutil.copy(bin_fp, build_lib)

  # Cleanup
  if made_build_temp:
    shutil.rmtree(build_temp)
  else:
    os.remove(tgz_filepath)
    shutil.rmtree(os.path.join(build_temp, 'vgmplay-0.40.8'))


class VGMPlayDevelop(develop):
  def run(self):
    develop.run(self)
    install_dir = os.path.join(self.install_dir, 'nesmdb')
    _build_vgm_play('/tmp/build_vgmplay', install_dir)


class VGMPlayInstall(install):
  def run(self):
    install.run(self)
    install_dir = os.path.join(self.install_lib, 'nesmdb')
    _build_vgm_play('/tmp/build_vgmplay', install_dir)


setup(
    name='nesmdb',
    version='0.1.8',
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
    cmdclass = {
      'develop': VGMPlayDevelop,
      'install': VGMPlayInstall,
    },
    entry_points = {
      'console_scripts': [
        'nesmdb_convert = nesmdb.convert:main',
      ],
    },
)
