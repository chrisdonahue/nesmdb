from setuptools import setup

setup(
    name='nesmdb',
    version='0.1',
    description='The NES Music Database (NES-MDB). Use machine learning to compose music for the Nintendo Entertainment System!',
    url='https://github.com/chrisdonahue/nesmdb',
    author='Chris Donahue',
    author_email='cdonahue@ucsd.edu',
    license='MIT',
    packages=['nesmdb'],
    keywords='music nes mir midi',
    install_requires=[
      'numpy >= 1.7.0',
      'scipy >= 1.0.0',
    ]
)
