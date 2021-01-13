#!/usr/bin/env python

from distutils.core import setup

setup(name='PyGrowatt',
      version='1.0',
      description='Growatt Server replacement implemented in Python',
      license='BSD-3-Clause',
      author='Aaron Brown',
      author_email='aaronjbrown@github.com',
      url='https://github.com/aaronjbrown/PyGrowatt',
      packages=['PyGrowatt'],
      install_requires=['pymodbus (>= 2.4.0)'],
      provides=['PyGrowatt'],
      )
