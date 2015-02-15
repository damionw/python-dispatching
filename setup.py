#!/usr/bin/env python

from setuptools import setup
from setuptools.command.test import test as TestCommand

package_name = 'dispatching'

class custom_tester(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True

    def run_tests(self):
        import unittest, sys

        test_loader = unittest.defaultTestLoader
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_suite = test_loader.discover('.') # WARNING: Only works for Python 2.7+
        test_runner.run(test_suite)

setup(
    name=package_name,
    version='0.1',
    description="Python Function Multiple Dispatching",
    author='Damion K. Wilson',
    include_package_data=True,
    test_suite='tests',
    platforms='any',

    cmdclass={
        'test': custom_tester,
    },

    install_requires=[
    ],

    packages=[
        package_name,
    ],

    package_dir={
        package_name: package_name,
    },
)
