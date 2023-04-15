#!/bin/bash

python -m isort bunnynet tests
python -m black --line-length 120 bunnynet tests
python -m pylint --rcfile=pylintrc bunnynet tests
python -m mypy --ignore-missing-imports bunnynet/ tests/
python -m bandit --configfile pyproject.toml -r bunnynet tests