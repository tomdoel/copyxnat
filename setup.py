# coding=utf-8
"""
Setup for copyxnat
"""

from setuptools import setup, find_packages
import versioneer
from copyxnat.utils.versioning import get_version
from os import path

version_git = get_version()

# Get the long description
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='copyxnat',
    version=version_git,
    cmdclass=versioneer.get_cmdclass(),
    description='CopyXnat is a python utility for copying XNAT projects from one XNAT server to another',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tomdoel/copyxnat',
    author='Tom Doel',
    license='MIT License',
    python_requires='>=2.7',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',

        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    keywords='medical imaging',

    packages=find_packages(include=['copyxnat', 'copyxnat.*']),

    install_requires=[
        'pyxnat>=1.4',
        'configparser==4.0.2',
        'urllib3>=1.26.3',
        'pydicom==1.4.2',
        'appdirs>=1.4.4',
        'lxml>=4.6.2',
        'xmltodict>=0.12.0',
        'six>=1.16.0',
        'enum34>=1.1.10'
    ],

    entry_points={
        'console_scripts': [
            'copyxnat=copyxnat.ui.command_line:run_entry_point',
        ],
    },
)
