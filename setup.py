#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Flask==0.12.2', 'requests==2.18.4']

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']

setup(
    author="Damian P.",
    author_email='an0o0nyme@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description=("Website Monitor is a program used for monitoring web sites "
                 "and reporting their availability."),
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='website_monitor',
    name='website_monitor',
    packages=find_packages(include=['website_monitor', 'web_app']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/an0o0nym/website_monitor',
    version='0.1.2',
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'website_monitor=website_monitor.website_monitor:main',
            'website_monitor_web_app=web_app.app:main'
        ],
    }
)
