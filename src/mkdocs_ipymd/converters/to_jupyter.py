import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from mkdocs_ipymd.converters.base import BaseConverter

__all__ = ["IPyToJupyter"]

class IPyToJupyter(BaseConverter):
    """
    Convert python file (according to VSCode Interative Python syntax) to Jupyter 
    notebook.
    """

    VALID_INPUT_EXTENSIONS = (".py", ".ipy")

    def __init__(self):
        ...

    def _convert(self, input_path : str, output_path : str):
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
        

    def parse_file(self, filepath : str):
        """Parse the file and extract the cells.
        
        Fill self.cells with the parsed cells.

        Args:
            filepath (str): the path to the file

        Returns:
            None
        """
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_cell_lines = []
        current_cell_type = "code"  # default cell type
        in_cell = False  # flag to check if we're inside a cell

        for line in lines:
            stripped_line = line.strip()

            if stripped_line.startswith("# %%"):
                # Save the previous cell if it exists
                if in_cell:
                    cell_content = "".join(current_cell_lines)
                    if current_cell_type == "code":
                        cell = new_code_cell(source=cell_content)
                    else:
                        cell = new_markdown_cell(source=cell_content)
                    self.cells.append(cell)
                    current_cell_lines = []
                # Determine the cell type for the new cell
                if stripped_line.startswith("# %% [markdown]"):
                    current_cell_type = "markdown"
                else:
                    current_cell_type = "code"
                in_cell = True
            else:
                # Add line to the current cell
                current_cell_lines.append(line)

        # Add the last cell if it exists
        if current_cell_lines:
            cell_content = "".join(current_cell_lines)
            if current_cell_type == "code":
                cell = new_code_cell(source=cell_content)
            else:
                cell = new_markdown_cell(source=cell_content)
            self.cells.append(cell)

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
