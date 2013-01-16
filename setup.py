#!/usr/bin/env python

import flaskmonitor

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


packages = ['flaskmonitor']
requires = [
        'flask==0.9',
        'python-cjson==1.0.5',
        'gevent==0.13.8',
        'numpy'
        ]


setup(
        name='flaskmonitor',
        version=flaskmonitor.__version__,
        description='Flask application to monitor running processes',
        long_description=open('README.md').read(),
        author='Luke Campbell',
        author_email='lcampbell@asascience.com',
        url='https://github.com/lukecampbell/flaskmonitor.git',
        packages=packages,
        package_data={'':['LICENSE']},
        include_package_data=True,
        install_requires=requires,
        license=open("LICENSE").read(),
        classifiers=(
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            ),
        entry_points = {
            'console_scripts': [
                'flaskmonitord = flaskmonitor.webapp:launch'
                ],
            },
        )



