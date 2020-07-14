# Conventions Linters

This guide will help you enforce Lego 3 conventions and prevent common mistakes.

## Pylint

Pylint is a Python static code analysis tool that looks for programming errors, helps to enforce a coding standard, sniffs for code smells and offers simple refactoring suggestions.

Install pylint:

```bash
python3.8 -m pip install pylint
```

Pylint your code:

```bash
python3.8 -m pylint --rcfile <pylintrc file path> <Octavius home dir>
```

## MyPy

Mypy is an optional static type checker for Python that aims to combine the benefits of dynamic (or "duck") typing and static typing.

We are using MyPy to enforce the developer to use the static typing feature, and avoid typing bugs in the code.

Install mypy:

```bash
python3.8 -m pip install mypy
```

Mypy your code:

```bash
python3.8 -m mypy --config-file <mypy.ini file path> <Octavius home dir>
```
