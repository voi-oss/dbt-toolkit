# dbt-toolkit

[![PyPI version](https://badge.fury.io/py/dbt-toolkit.svg)](https://badge.fury.io/py/dbt-toolkit)
[![Tests](https://github.com/voi-oss/dbt-toolkit/actions/workflows/run-tests.yaml/badge.svg)](https://github.com/voi-oss/dbt-toolkit/actions/workflows/run-tests.yaml)
[![Code checks](https://github.com/voi-oss/dbt-toolkit/actions/workflows/run-code-checks.yaml/badge.svg)](https://github.com/voi-oss/dbt-toolkit/actions/workflows/run-code-checks.yaml)
[![codecov](https://codecov.io/gh/voi-oss/dbt-toolkit/branch/main/graph/badge.svg?token=5JS1RLYRQF)](https://codecov.io/gh/voi-oss/dbt-toolkit)
[![Apache License 2.0](https://img.shields.io/github/license/voi-oss/dbt-toolkit)](https://github.com/voi-oss/dbt-toolkit)

A collection of utilities and tools for teams and organizations using dbt.

> This project is in an ALPHA stage. Internal and external APIs might change between minor versions.

> Please reach out if you try this at your own organization. Feedback is very appreciated, and we
> would love to hear if you had any issues setting this up at your own.

## Automations

### Documentation

* Propagates the documentation of columns that have the same name on downstream models, improving documentation
coverage while reducing manual repeated work

More information can be found on the package's [README](src/dbttoolkit/documentation/README.md).

### dbt Cloud artifacts

* Retrieve artifacts from a dbt Cloud project. Useful for building reports (such as test and documentation coverage)

More information can be found on the package's [README](src/dbttoolkit/dbt_cloud/README.md).

## Installation

This project requires Python 3.8+. You can install the latest version of this package from PyPI by running the 
command below.

```shell
$ pip install dbt-toolkit
```

## Development

### Contributing

We are open and would love to have contributions, both in Pull Requests but also in ideas and feedback. Don't hesitate
to create an Issue on this repository if you are trying this project in your organization or have anything to share.

Remember to run `make lint`, `make type` and `make test` before committing.

Run `make install-dev` to install it locally in editable mode. This is necessary for running the tests.

### Architecture

Groups of functionalities are encapsulated together in top-level packages, such as `dbt_cloud/` or `documentation/`.
Each package that exposes CLI commands should contain an `actions` sub-package. 

## Tests

More information can be found on the tests' [README](tests/README.md).

## Release

There is a GitHub Action that will trigger a release of this package on PyPI based on releases created on GitHub.
Steps:

* Loosely follow [semantic versioning](https://semver.org/)
* Remember to prefix the tag name with `v`
* Use the tag name as the release title on GitHub
* Use the auto-generated release notes from GitHub
* Append a link at the end of the release notes to the released version on PyPI

## License

This project is licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.
