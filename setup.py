from setuptools import setup
from codecs import open
from os import path, system
import sys

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


tests_deps = [
    "nose",
    "retry",
]

extras = {"tests": tests_deps, "docs": "sphinx"}

setup(
    name="xaccount",
    description="Library designed for easy, automatic and secure operations on popular websites - sign up user accounts, etc.",
    long_description=long_description,
    url="https://github.com/xaccount/xaccount",
    author="xaccount",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    test_suite="tests",
    use_scm_version=True,
    setup_requires=["setuptools_scm", "wheel"],
    keywords="recaptcha captcha development",
    packages=["python_anticaptcha"],
    install_requires=["requests", "Faker", "selenium", "dateutil", "phonenumbers"],
    tests_require=tests_deps,
    extras_require=extras,
)
