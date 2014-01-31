#!/usr/bin/env python
import os.path

from setuptools import find_packages, setup


def readme():
    path = os.path.join(os.path.dirname(__file__), 'README.rst')
    with open(path) as f:
        return f.read()


def stripped_reqs(fd):
    return (l.strip() for l in fd)


def parse_requirements(requirements):
    with open(requirements) as f:
        return [l for l in stripped_reqs(f) if l and not l.startswith('#')]


setup(name='zenconf',
      version='0.1.3',
      description='Simple configuration system based on recursively merging '
                  'dicts.',
      long_description=readme(),
      url='https://github.com/nws-cip/zenconf',
      author='Alan Bates',
      author_email='alan.bates@news.co.uk',
      license='MIT',
      packages=find_packages(),
      install_requires=['funcy==0.9'],
      zip_safe=True)
