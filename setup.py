#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

# TODO: this is stupid, don't read here :-/
readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

test_requires = ['moto', 'nose']

setup(
    name='zing',
    version='0.1.0',
    description='Database writes via SQS',
    long_description=readme + '\n\n' + history,
    author='Christopher Grebs',
    author_email='cg@webshox.org',
    url='https://github.com/EnTeQuAk/zing',
    packages=[
        'zing',
    ],
    package_dir={'zing': 'zing'},
    include_package_data=True,
    install_requires=[
        'Django>=1.6,<1.7',
        'gevent>=1.0',
        'boto>=2.19.0',
    ],
    tests_require=test_requires,
    extras_require={
        'docs': ['sphinx'],
        'tox': ['tox'],
        'tests': test_requires
    },
    entry_points={
        'console_scripts': [
            'zing = zing.cli:main',
        ]
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='nose.collector',
)
