""" Setup script for the paneldata_pipeline package."""
from setuptools import find_packages, setup

with open("./README.md", encoding="utf8") as readme:
    LONG_DESCRIPTION = readme.read()

setup(
    author="Dominique Hansen",
    author_email="dhansen@diw.de",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
    ],
    description="Process data for the import into a ddionrails instance.",
    entry_points={
        "console_scripts": [
            "paneldata_pipeline=paneldata_pipeline.__main__:main",
            "paneldata_relation_checks=paneldata_pipeline.check_relations:main",
        ]
    },
    install_requires=[
        "pandas==1.4.3",
        "frictionless==4.40.3",
        "tabulate==0.8.10",
    ],
    include_package_data=True,
    keywords=["preprocessing", "ddionrails", "paneldata", "csv", "humanities"],
    long_description=LONG_DESCRIPTION,
    name="paneldata_pipeline",
    packages=find_packages(),
    package_data={"resources": ["paneldata_pipline/resources/*.json"]},
    python_requires=">=3.6.0",
    url="https://github.com/ddionrails/paneldata_pipeline.git",
    version="0.1.0",
)
