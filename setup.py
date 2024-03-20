# -*- coding:utf-8 -*-
import codecs
import os
import sys
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def readfile(fname):
    return codecs.open(os.path.join(here, fname), encoding='utf-8').read()


version = '0.10.0'

README = readfile('README.rst')
CHANGES = readfile('CHANGES.rst')
AUTHORS = readfile('AUTHORS.rst')

install_requires = []

# hack, or test wont run on py2.7
try:
    import multiprocessing
    import logging
except:
    pass

setup(name='wsgicoers',
      version=version,
      description="WSGI for Cross Origin Resource Sharing (CORS)",
      long_description=README + '\n\n' + CHANGES + '\n\n' + AUTHORS,
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Development Status :: 3 - Alpha",
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Internet :: WWW/HTTP :: WSGI"
      ],
      keywords=["wsgi", "cors"],
      author='Norman Krämer',
      author_email='kraemer.norman@googlemail.com',
      url="https://github.com/may-day/wsgicors",
      license='Apache Software License 2.0',
      py_modules=["wsgicoers"],
      install_requires=install_requires,
      tests_require=[
          'nose',
          'nose-testconfig',
          'webob'
      ],
      test_suite='nose.collector',
      entry_points="""
      [paste.filter_app_factory]
      middleware = wsgicoers:make_middleware
      """
      )
