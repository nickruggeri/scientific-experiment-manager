from pathlib import Path

from setuptools import setup

# README reading for information.
# See https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="scientific-experiment-manager",
    version="0.1.0",
    packages=["sem"],
    project_urls={
        "Source": "https://github.com/nickruggeri/scientific-experiment-manager",
        "Documentation": "https://github.com/nickruggeri/scientific-experiment-manager",
    },
    license="MIT",
    author="Nicolò Ruggeri",
    author_email="nicolo.ruggeri@tuebingen.mpg.de",
    install_requires=[
        "numpy >= 1.23.0",
        "pandas >= 1.5.0",
    ],
    description="SEM: streamline your scientific experiment management",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
