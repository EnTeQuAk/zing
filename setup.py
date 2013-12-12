#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

with open('README.rst') as fobj:
    readme = fobj.read()

with open('HISTORY.rst') as fobj:
    history = fobj.read()
    history.replace('.. :changelog:', '')


test_requires = [
    'moto',
    'nose',
    'coverage',
    'pytest',
    'pytest-cov>=1.4',
    'pytest-django',
    'python-coveralls',
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

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
        'django-appconf',
        'gevent>=1.0',
        'boto>=2.19.0',
    ],
    tests_require=test_requires,
    cmdclass={'test': PyTest},
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
)
