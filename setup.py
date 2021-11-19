import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="pyToledo-test2",
    version="0.0.23",
    description="pyToledo is a Python library to interact with the common virtual learning environment for the Association KU Leuven (Toledo).",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/DaanVervacke/pyToledo",
    author="Vervacke Daan",
    author_email="daan.vervacke@student.vives.be",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["requests", "beautifulsoup4", "pkce", "soupsieve"]

)
