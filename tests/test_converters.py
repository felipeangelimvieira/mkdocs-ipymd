# test_converters.py

import os
from pathlib import Path

import nbformat
import pytest
from nbformat import v4 as nbf

from mkdocs_ipymd.converters import IPyToJupyter, JupyterToMarkdown
# Assuming the converters are accessible via the following imports
from mkdocs_ipymd.converters.base import BaseConverter, SequentialConverter


@pytest.fixture
def sample_python_file(tmp_path):
    """
    Create a sample .py file with VSCode Interactive Python syntax.
    """
    content = """
# %%
print("Hello from cell 1")

# %% [markdown]
# This is a markdown cell.

# %%
print("Hello from cell 2")
"""
    file_path = tmp_path / "sample.py"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_notebook_file(tmp_path):
    """
    Create a sample .ipynb file.
    """
    nb = nbf.new_notebook()
    nb.cells = [
        nbf.new_code_cell("print('Hello from notebook')"),
        nbf.new_markdown_cell("# This is a markdown cell in notebook"),
    ]
    file_path = tmp_path / "sample.ipynb"
    with open(file_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    return file_path


def test_ipy_to_jupyter(sample_python_file, tmp_path):
    """
    Test that IPyToJupyter converts a .py file to a .ipynb notebook correctly.
    """
    converter = IPyToJupyter()
    output_file = tmp_path / "output.ipynb"
    converter.convert(str(sample_python_file), str(output_file))
    assert output_file.exists()

    # Load the output notebook and check its content
    with open(output_file, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    assert len(nb.cells) == 3
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source.strip() == 'print("Hello from cell 1")'
    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[1].source.strip() == "# This is a markdown cell."
    assert nb.cells[2].cell_type == "code"
    assert nb.cells[2].source.strip() == 'print("Hello from cell 2")'


def test_jupyter_to_markdown(sample_notebook_file, tmp_path):
    """
    Test that JupyterToMarkdown converts a .ipynb notebook to a .md file without executing it.
    """
    converter = JupyterToMarkdown(execute=False)
    output_file = tmp_path / "output.md"
    converter.convert(str(sample_notebook_file), str(output_file))
    assert output_file.exists()

    # Check that the markdown file contains the expected content
    content = output_file.read_text()
    assert "# This is a markdown cell in notebook" in content
    assert "print('Hello from notebook')" in content


def test_jupyter_to_markdown_execute(sample_notebook_file, tmp_path):
    """
    Test that JupyterToMarkdown executes the notebook before converting to Markdown.
    """
    converter = JupyterToMarkdown(execute=True)
    output_file = tmp_path / "output.md"
    converter.convert(str(sample_notebook_file), str(output_file))
    assert output_file.exists()

    # Check that the output from the executed code is in the markdown
    content = output_file.read_text()
    assert "# This is a markdown cell in notebook" in content
    assert "Hello from notebook" in content  # Output from the code cell


def test_sequential_converter(sample_python_file, tmp_path):
    """
    Test that SequentialConverter chains IPyToJupyter and JupyterToMarkdown correctly.
    """
    converter_py_to_ipynb = IPyToJupyter()
    converter_ipynb_to_md = JupyterToMarkdown(execute=False)
    sequential_converter = converter_py_to_ipynb >> converter_ipynb_to_md
    output_file = tmp_path / "output.md"
    sequential_converter.convert(str(sample_python_file), str(output_file))
    assert output_file.exists()
    content = output_file.read_text()
    assert "# This is a markdown cell." in content
    assert 'print("Hello from cell 1")' in content
    assert 'print("Hello from cell 2")' in content


def test_sequential_converter_execute(sample_python_file, tmp_path):
    """
    Test SequentialConverter with execution of the notebook.
    """
    converter_py_to_ipynb = IPyToJupyter()
    converter_ipynb_to_md = JupyterToMarkdown(execute=True)
    sequential_converter = converter_py_to_ipynb >> converter_ipynb_to_md
    output_file = tmp_path / "output.md"
    sequential_converter.convert(str(sample_python_file), str(output_file))
    assert output_file.exists()
    content = output_file.read_text()
    assert "# This is a markdown cell." in content
    assert "Hello from cell 1" in content  # Output from executing the code cell
    assert "Hello from cell 2" in content


def test_base_converter_validation(tmp_path):
    """
    Test that BaseConverter's validation works correctly.
    """

    # Create a dummy subclass of BaseConverter to test validation
    class DummyConverter(BaseConverter):
        VALID_INPUT_EXTENSIONS = (".txt",)

        def _convert(self, input_path, output_path):
            pass

        def get_output_extension(self):
            return ".out"

    converter = DummyConverter()

    # Create a valid input file
    valid_file = tmp_path / "valid.txt"
    valid_file.write_text("Test content")

    # This should pass
    converter.convert(str(valid_file), str(tmp_path / "output.out"))

    # Create an invalid input file
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("Test content")

    # This should raise ValueError due to invalid extension
    with pytest.raises(ValueError):
        converter.convert(str(invalid_file), str(tmp_path / "output.out"))

    # Non-existent file should raise FileNotFoundError
    nonexistent_file = tmp_path / "nonexistent.txt"
    with pytest.raises(FileNotFoundError):
        converter.convert(str(nonexistent_file), str(tmp_path / "output.out"))


def test_ipy_to_jupyter_invalid_extension(tmp_path):
    """
    Test that IPyToJupyter raises ValueError when given an invalid file extension.
    """
    converter = IPyToJupyter()
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("# %%\nprint('Hello')")
    with pytest.raises(ValueError):
        converter.convert(str(invalid_file), str(tmp_path / "output.ipynb"))


def test_jupyter_to_markdown_invalid_extension(tmp_path):
    """
    Test that JupyterToMarkdown raises ValueError when given an invalid file extension.
    """
    converter = JupyterToMarkdown(execute=False)
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("Invalid content")
    with pytest.raises(ValueError):
        converter.convert(str(invalid_file), str(tmp_path / "output.md"))
