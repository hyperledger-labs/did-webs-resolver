#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
$ python setup.py register sdist upload

First Time register project on pypi
https://pypi.org/manage/projects/


Pypi Release
$ pip3 install twine

$ python3 setup.py sdist
$ twine upload dist/keri-0.0.1.tar.gz

Create release git:
$ git tag -a v0.4.2 -m "bump version"
$ git push --tags
$ git checkout -b release_0.4.2
$ git push --set-upstream origin release_0.4.2
$ git checkout master

Best practices for setup.py and requirements.txt
https://caremad.io/posts/2013/07/setup-vs-requirement/
"""

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages, setup

setup(
    name='dkr',
    version='0.0.1',  # also change in src/did-keri-resolver/__init__.py
    license='Apache Software License 2.0',
    description='did:keri DID Method Resolver',
    long_description="did:keri DID Method Resolver.",
    author='Philip S. Feairheller',
    author_email='pfeairheller@gmail.com',
    url='https://github.com/WebOfTrust/kara',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://kara.readthedocs.io/',
        'Changelog': 'https://kara.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/WebOfTrust/kara/issues',
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.10.4',
    install_requires=[
                        'lmdb>=1.3.0',
                        'pysodium>=0.7.12',
                        'blake3>=0.3.1',
                        'msgpack>=1.0.4',
                        'cbor2>=5.4.3',
                        'multidict>=6.0.2',
                        'ordered-set>=4.1.0',
                        'hio>=0.6.9',
                        'multicommand>=1.0.0',
                        'jsonschema>=4.17.0',
                        'falcon>=3.1.0',
                        'hjson>=3.0.2',
                        'PyYaml>=6.0',
                        'apispec>=6.0.0',
                        'mnemonic>=0.20',
                        'PrettyTable>=3.5.0',
                        'http_sfv>=0.9.8',
                        'cryptography>=39.0.2',
                        'numpy>=1.26.0'
    ],
    extras_require={
    },
    tests_require=[
        'coverage>=5.5',
        'pytest>=6.2.5',
    ],
    setup_requires=[
    ],
    entry_points={
        'console_scripts': [
            'dkr = dkr.app.cli.dkr:main',
        ]
    },
)
