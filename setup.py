from setuptools import setup

setup(
    name='nesmdb',
    version='0.1.2',
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
)
