if (-not $env:FOO) {
    .\venv\Scripts\Activate.ps1
}

python -m isort restapi tests
python -m black --line-length 120 restapi tests
python -m pylint --rcfile=pylintrc restapi tests
python -m mypy --ignore-missing-imports restapi/ tests/
python -m bandit --configfile pyproject.toml -r restapi tests