import os
from setuptools import setup, find_packages

# Read the README.md file for the long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="PapAiEra",
    version="0.2.1",
    description="A Python library for Pulp and Paper manufacturing processes, based on BREF (Best Available Techniques) standards.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PapAiEra",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Manufacturing",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    python_requires='>=3.6',
)
