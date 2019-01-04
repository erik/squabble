from setuptools import setup

__version__ = '1.0.0rc1'


setup(
    name='squabble',
    version=__version__,
    description='An extensible linter for SQL',
    author='Erik Price',
    url='https://github.com/erik/squabble',
    packages=['squabble'],
    entry_points={
        'console_scripts': [
            'squabble = squabble.__main__:main',
        ],
    },
    python_requires='>=3.5',
    license='GPLv3+',
    install_requires=[
        'pglast==1.1',
        'docopt==0.6.2',
        'colorama==0.4.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: SQL'
    ]
)
