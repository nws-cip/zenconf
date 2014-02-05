#!/usr/bin/env python
import os.path

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


def readme():
    path = os.path.join(os.path.dirname(__file__), 'README.rst')
    if os.path.exists(path):
        with open(path) as f:
            return f.read()


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(name='zenconf',
      version='0.1.4',
      description='Simple configuration system based on recursively merging '
                  'dicts.',
      long_description=readme(),
      url='https://github.com/nws-cip/zenconf',
      author='Alan Bates',
      author_email='alan.bates@news.co.uk',
      license='MIT',
      packages=find_packages(),
      install_requires=['funcy==0.9'],
      tests_require=['tox'],
      cmdclass = {'test': Tox},
      zip_safe=True)
