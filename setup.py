# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
from setuptools import setup, find_packages

def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''

# Use the docstring of the __init__ file to be the description
DESC = " ".join(__import__('geocamMemo').__doc__.splitlines()).strip()

setup(
    name = "geocamMemoWeb",
    version = __import__('geocamMemo').get_version().replace(' ', '-'),
    url = '',
    author = 'GeoCam Project',
    author_email = '',
    description = DESC,
    long_description = read_file('README'),
    packages = find_packages(),
    include_package_data = True,
    install_requires=read_file('requirements.txt'),
    classifiers = [
        'License :: OSI Approved :: NASA Open Source Agreement',
        'Framework :: Django',
    ],
)
