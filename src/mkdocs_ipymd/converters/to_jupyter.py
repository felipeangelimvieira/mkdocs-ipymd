import json
import re

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from mkdocs_ipymd.converters.base import BaseConverter

__all__ = ["IPyToJupyter"]


class IPyToJupyter(BaseConverter):
    """
    Convert a Python file (with VSCode Interactive Python syntax) to a Jupyter notebook.
    Supports extended syntax for cell metadata using JSON after the cell marker.

    Example:
        # %% {tags=["hide-code"]}

    """

    VALID_INPUT_EXTENSIONS = (".py", ".ipy")

    def __init__(self):
        pass  # No changes needed here

    def _convert(self, input_path: str, output_path: str):
        """Convert python file to Jupyter notebook.

        Args:
            input_path (str): the path to the input file
            output_path (str): the path to the output file

        Returns:
            None
        """
        self.cells = []
        self.parse_file(input_path)
        self.create_notebook()
        nbformat.write(self.notebook, output_path)

    def parse_file(self, filepath: str):
        """Parse the file and extract the cells.

        Fills self.cells with the parsed cells.

        Args:
            filepath (str): the path to the file

        Returns:
            None
        """
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_cell_lines = []
        current_cell_type = "code"  # default cell type
        current_cell_metadata = {}  # Initialize cell metadata
        in_cell = False  # flag to check if we're inside a cell

        # Regular expression to match the cell marker and extract JSON
        cell_marker_regex = re.compile(r"^# %%\s*(.*)")

        for line in lines:
            stripped_line = line.strip()

            match = cell_marker_regex.match(stripped_line)
            if match:
                # Save the previous cell if it exists
                if in_cell:
                    cell_content = "".join(current_cell_lines)
                    if current_cell_type == "code":
                        cell = new_code_cell(
                            source=cell_content, metadata=current_cell_metadata
                        )
                    else:
                        cell = new_markdown_cell(
                            source=cell_content, metadata=current_cell_metadata
                        )
                    self.cells.append(cell)
                    current_cell_lines = []
                    current_cell_metadata = {}  # Reset metadata for the new cell

                # Process the cell marker
                metadata_str = match.group(1).strip()
                if metadata_str.startswith("[markdown]"):
                    current_cell_type = "markdown"
                    # Check for metadata after [markdown]
                    metadata_json_str = metadata_str[len("[markdown]") :].strip()
                    if metadata_json_str:
                        current_cell_metadata = self._parse_metadata(
                            metadata_json_str, line
                        )
                else:
                    current_cell_type = "code"
                    if metadata_str:
                        current_cell_metadata = self._parse_metadata(metadata_str, line)

                in_cell = True
            else:
                # Add line to the current cell
                current_cell_lines.append(line)

        # Add the last cell if it exists
        if current_cell_lines:
            cell_content = "".join(current_cell_lines)
            if current_cell_type == "code":
                cell = new_code_cell(
                    source=cell_content, metadata=current_cell_metadata
                )
            else:
                cell = new_markdown_cell(
                    source=cell_content, metadata=current_cell_metadata
                )
            self.cells.append(cell)

    def _parse_metadata(self, metadata_str, line):
        """Parse the JSON metadata from the cell marker.

        Args:
            metadata_str (str): The string containing JSON metadata.
            line (str): The original line for error reporting.

        Returns:
            dict: Parsed metadata dictionary.
        """
        try:
            # Try parsing the metadata string as JSON
            metadata = json.loads(metadata_str)
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a JSON object (dictionary).")
            return metadata
        except json.JSONDecodeError as e:
            print(
                f"Warning: Failed to parse cell metadata in line: '{line.strip()}'. Error: {e}"
            )
            raise e
            return {}
        except ValueError as e:
            print(f"Warning: {e} in line: '{line.strip()}'.")
            raise e
            return {}

    def create_notebook(self):
        """Create a new Jupyter notebook with the parsed cells."""
        self.notebook = new_notebook(cells=self.cells)

    def execute_notebook(self):
        """Execute the notebook in-place."""
        client = NotebookClient(self.notebook, timeout=600)
        client.execute()

    def get_output_extension(self):
        """Return the output extension of the converter."""
        return ".ipynb"
