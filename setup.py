#!/usr/bin/env python3

from setuptools import setup
from pathlib import Path
setup_dir = Path(__file__).parent

setup(
    name='keybox',
    version=(setup_dir / 'VERSION').read_text().strip(),
    description='Storage for passwords, encrypted with GPG',
    long_description=(setup_dir / "README.rst").read_text(),
    long_description_content_type='text/x-rst',
    author='Radek Brich',
    author_email='radek.brich@devl.cz',
    license='MIT',
    url='https://github.com/rbrich/keybox',
    packages=['keybox'],
    entry_points={
        'console_scripts': [
            'keybox = keybox.main:main',
        ],
    },
    setup_requires=['pytest-runner'],
    install_requires=['blessed'],
    tests_require=['pytest', 'pexpect'],
)
