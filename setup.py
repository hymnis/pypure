import sys
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pypurea9",
    version="0.1.0",
    description="Python3 API for the Electrolux Pure A9 air purifier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hymnis/pypurea9",
    author="hymnis",
    author_email="hymnis@plazed.net",
    classifiers=[
        "License :: MIT",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    keywords="automation purea9",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.5",
    install_requires=["requests"],
    entry_points={"console_scripts": ["purea9=pypurea9.pypurea9:main"]},
    project_urls={
        "Source": "https://github.com/hymnis/pypurea9",
        "Bug Reports": "https://github.com/hymnis/pypurea9/issues",
    },
)
