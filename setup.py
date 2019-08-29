""" Setup script for the paneldata_pipeline package."""
from setuptools import find_packages, setup

setup(
    author="Dominique Hansen",
    author_email="dhansen@diw.de",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
    ],
    description="Process data for the import into a ddionrails instance.",
    install_requires=[],
    keywords=["preprocessing", "ddionrails", "paneldata", "csv", "humanities"],
    long_description=open("./README.md").read(),
    name="paneldata_pipeline",
    packages=find_packages(),
    python_requires=">=3.6.0",
    url="https://github.com/ddionrails/paneldata_pipeline.git",
    version="0.0.1",
)
