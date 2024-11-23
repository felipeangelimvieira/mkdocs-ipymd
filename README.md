# Mkdocs-Ipymd

<p align="center">
<img src="logo.png" width="200">

</p>

[![PyPI version](https://badge.fury.io/py/mkdocs-ipymd.svg)](https://badge.fury.io/py/prophetverse)
[![codecov](https://codecov.io/gh/felipeangelimvieira/mkdocs-ipymd/graph/badge.svg?token=O37PGJI3ZX)](https://codecov.io/gh/felipeangelimvieira/mkdocs-ipymd)


# Mkdocs plugin for Interactive Python

This plugin allows you to use python, in VSCode interactive fashion, to create docs.
The motivation was having a way to create interactive examples in the documentation,
without increasing the git repository size.

## Installation

```bash
pip install mkdocs-ipymd
```

or with poetry:

```bash
poetry add mkdocs-ipymd
```

## Usage

### 1. Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - ipymd
```

### 2. Create a python file ".py" or ".ipy" in the `docs` folder:

And use the following syntax to include the file in your markdown:

```python
# %%
import numpy as np
import matplotlib.pyplot as plt

# %%
msg = "Hello World"
print(msg)

# %%
msg = "Hello not again"
print(msg)

# %% [markdown]

## This is a markdown cell

### With some content

And some math

$$
E = mc^2
$$
```

The `# %%` is a cell separator, and the content of the cell is executed as python code.

### 3. Add the file to your `mkdocs.yml` nav (optional)

```yaml
nav:
  - Home: index.md
  - Examples:
    - file1.md
    - file2.md
```

Important: you must add the file with ".md" extension, even if the file is a python 
file.