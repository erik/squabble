import os.path

from setuptools import setup, find_packages

__version__ = '1.3.2'


readme_path = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readme_path) as fp:
    long_description = fp.read()

setup(
    name='squabble',
    version=__version__,
    description='An extensible linter for SQL',
    long_description=long_description,
    author='Erik Price',
    url='https://github.com/erik/squabble',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'squabble = squabble.__main__:main',
        ],
    },
    python_requires='>=3.5',
    license='GPLv3+',
    setup_requires=[
        'pytest-runner',
    ],
    install_requires=[
        'pglast==1.4',
        'docopt==0.6.2',
        'colorama==0.4.1'
    ],
    tests_require=[
        'pytest',
        'pytest-runner',
        'pytest-cov',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: SQL',
        'Topic :: Utilities',
    ]
)
