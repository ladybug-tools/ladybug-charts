[![Build Status](https://github.com/ladybug-tools/ladybug-charts/workflows/CI/badge.svg)](https://github.com/ladybug-tools/ladybug-charts/actions)

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

# ladybug-charts

Ladybug extension to generate 2D charts.

## Installation
```console
pip install ladybug-charts
```

## QuickStart
```python
import ladybug_charts

```

## [API Documentation](http://ladybug-tools.github.io/ladybug-charts/docs)

## Local Development
1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/ladybug-charts

# or

git clone https://github.com/ladybug-tools/ladybug-charts
```
2. Install dependencies:
```console
cd ladybug-charts
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./ladybug_charts
sphinx-build -b html ./docs ./docs/_build/docs
```

## Credits:
This project is a derivative work of [Clima](https://clima.cbe.berkeley.edu/) which is available under an MIT license. We are grateful to the developers of the original work.