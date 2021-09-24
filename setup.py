#!/usr/bin/env python
"""
sde
==========
.. code:: shell
  $ sde name Jack data.json
  $ sde name Jack data.yml
"""

from setuptools import find_packages, setup
import os
import re

_version_re = re.compile(r"__version__\s=\s'(.*)'")

install_requires = [
    "six"
]
tests_requires = [
    "pytest>=4.4.0",
    "flake8",
    # somehow getting this issue only in Travis, anyway this should fix:
    # https://github.com/pytest-dev/pytest/issues/6887#issuecomment-600979770
    "pytest-xdist==1.29.0"
]

docs_requires = [
    "mkdocs==1.1.2",
    "mkdocs-material",
    "mkdocstrings",
    "markdown-include"
]

with open("README.md", "r") as fh:
    long_description = fh.read()

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, "sde", "__about__.py"), 'r') as f:
    version = _version_re.search(f.read()).group(1)

setup(
    name="sde",
    version=version,
    author="Danila Vershinin",
    author_email="info@getpagespeed.com",
    url="https://github.com/dvershinin/sde",
    description="A CLI tool to edit simple JSON and YAML data files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "docs"]),
    zip_safe=False,
    license="BSD",
    install_requires=install_requires,
    extras_require={
        "tests": install_requires + tests_requires,
        "docs": docs_requires,
        "build": install_requires + tests_requires + docs_requires,
    },
    tests_require=tests_requires,
    include_package_data=True,
    entry_points={"console_scripts": ["sde = sde:main"]},
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Utilities"
    ],
)
