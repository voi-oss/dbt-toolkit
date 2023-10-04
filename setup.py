import pathlib

from setuptools import find_packages, setup

# Get the long description from the README file
current_folder = pathlib.Path(__file__).parent.resolve()
long_description = (current_folder / "README.md").read_text(encoding="utf-8")

# Based on: https://packaging.python.org/tutorials/packaging-projects/
setup(
    name="dbt-toolkit",
    use_scm_version={
        "write_to": "src/dbttoolkit/_version.py",
        "write_to_template": '__version__ = "{version}"\n',
        "local_scheme": "no-local-version",
        "fallback_version": "0+unknown.scm_missing",
    },
    description="Utilities for running dbt automations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/voi-oss/dbt-toolkit",
    author="Voi Technology AB",
    author_email="opensource@voiapp.io",
    license="Apache License, Version 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    scripts=["bin/dbt-toolkit"],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8, <4",
    setup_requires=["wheel", "setuptools_scm"],
    install_requires=[
        "requests ~= 2.28.0",
        "typer ~= 0.4.2",
        "google-cloud-storage ~= 2.4.0",
        "pydantic ~= 1.9.1",
        "rich ~= 13.3.5",
    ],
)
