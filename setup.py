from setuptools import setup

setup(
    name='nesmdb',
    version='0.1.0',
    description='The NES Music Database (NES-MDB). Use machine learning to compose music for the Nintendo Entertainment System!',
    url='https://github.com/chrisdonahue/nesmdb',
    author='Chris Donahue',
    author_email='cdonahue@ucsd.edu',
    license='MIT',
    packages=['nesmdb', 'nesmdb.vgm'],
    keywords='music nes mir midi',
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
    ]
)
