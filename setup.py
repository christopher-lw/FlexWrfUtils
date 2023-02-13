#!/usr/bin/env python

import setuptools

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f.readlines()]

setuptools.setup(
    name="flexwrfutils",
    version="0.2",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=requirements,
)
