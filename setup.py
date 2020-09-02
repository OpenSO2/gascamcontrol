import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "readme.md").read_text()
VERSION = (HERE / "gascamcontrol/_version.txt").read_text()

# This call to setup() does all the work
setup(
    name="gascamcontrol",
    version=VERSION,
    description="",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Johann Jacobsohn",
    author_email="johann.jacobsohn@uni-hamburg.de",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        'Development Status :: 1 - Planning',
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "gascamcontrol=gascamcontrol.gascamcontrol:main",
        ]
    },
)
