# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def readme():
    """
    Get description from README file
    :return: README content
    """
    with open('README.md') as f:
        return f.read()


def get_requirements_from_files():
    """
    Collect all dependencies required to run the project from requirements files
    :return: a list of required packages
    """
    with open('requirements.txt', 'r') as pypi_lines:
        requirement_list = pypi_lines.readlines()

    return [elt for elt in requirement_list]


setup(
    name='ds_toolbox',
    packages=find_packages(),
    version='0.1.0',
    description='Tools to perform Data Science study',
    long_description=readme(),
    license='TOBEDEFINED',
    install_requires=get_requirements_from_files(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=False,
    include_package_data=True
)
