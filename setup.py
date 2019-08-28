""" Setup script for the paneldata_pipeline package."""
from setuptools import find_packages, setup

setup(
    name="paneldata_pipeline",
    version="0.0.1",
    url="https://github.com/ddionrails/paneldata_pipeline.git",
    description="Process data for the import into a ddionrails instance.",
    long_description=open("./README.md").read(),
    packages=find_packages(),
    install_requires=[],
)
