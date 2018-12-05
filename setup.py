from setuptools import setup


__version__ = '0.0.0'


setup(
    name='squabble',
    version=__version__,
    description='TODO',
    author='Erik Price',
    url='https://github.com/erik/squabble',
    packages=['squabble'],
    entry_points={
        'console_scripts': [
            'squabble = squabble:main',
        ],
    },
    license='GPLv3+',
    install_requires=[
        'pglast==1.1',
        'docopt==0.6.2'
    ]
)
