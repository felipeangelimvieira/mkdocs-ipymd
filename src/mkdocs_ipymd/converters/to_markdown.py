import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbconvert import MarkdownExporter
from nbconvert.writers import FilesWriter

from mkdocs_ipymd.converters.base import BaseConverter

__all__ = ["JupyterToMarkdown"]


class JupyterToMarkdown(BaseConverter):
    """"Convert Jupyter notebook to Markdown.
    
    Parameters
    ----------
    execute: bool, optional
        Whether to execute the notebook before converting to Markdown. Default is False.
    template_file: str, optional
        Path to a custom template file to use for the conversion.
        Default is None, which uses the default template
    """

    VALID_INPUT_EXTENSIONS = (".ipynb",)

    def __init__(self, execute=False, template_file=None):

        self.execute = execute
        self.template_file = template_file
        super().__init__()
        self.notebook = None  # Will hold the notebook object after loading
        self.generated_files = []  # List to store generated files
        if template_file is None:
            self._template = Path(__file__).parent / Path("templates/default_template.tpl")
        else:
            self._template = Path(template_file)

    def _convert(self, input_path : str, output_path : str):
        """Convert Jupyter notebook to Markdown.

        Parameters
        ----------
        input_path : str
            the path to the input file
        output_path : str
            the path to the output file

        Returns
        -------
        None
        """
        self.notebook_path = input_path
        self.load_notebook()
        self.update_kernelspec()
        if self.execute:
            self.execute_notebook()
        self.convert_to_markdown(output_path)

    def load_notebook(self):
        """Load the notebook from the file system."""
        with open(self.notebook_path, "r", encoding="utf-8") as f:
            self.notebook = nbformat.read(f, as_version=4)
        print(f"Notebook loaded from {self.notebook_path}")

    def update_kernelspec(self):
        """Update the notebook's kernelspec to use sys.executable."""
        self.notebook.metadata["kernelspec"] = {
            "display_name": f"Python ({sys.executable})",
            "language": "python",
            "name": "python",
            "argv": [
                sys.executable,
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
        }
        print(f"Kernelspec updated to use sys.executable: {sys.executable}")

    def execute_notebook(self):
        """Execute the notebook in-place."""
        print("Executing notebook...")
        print("Kernel:", sys.executable)
        client = NotebookClient(self.notebook, timeout=600, kernel_name="python")
        client.execute()
        print("Notebook execution completed.")

    def convert_to_markdown(self, output_path=None):
        """
        Convert the notebook to a Markdown file.

        Ensures images and other resources are saved.

        Parameters
        ----------
        output_path : str, optional
            Path to save the output .md file. If None, saves in the same directory
            with the same name.
        output_path (str): Path to save the output .md file. 
            If None, saves in the same directory with the same name.
        """
        # Code below 70% by chatgpt ;)
        
        print("Converting notebook to Markdown...")

        # Use the custom template if provided
        if self._template:
            # Create an exporter with the custom template
            exporter = MarkdownExporter(template_file=str(self._template))
        else:
            exporter = MarkdownExporter()

        # Set up resources
        resources = {}
        # Determine the output path and base name
        if output_path is None:
            dir_name = os.path.dirname(self.notebook_path)
            base_name = os.path.splitext(os.path.basename(self.notebook_path))[0]
            output_path = os.path.join(dir_name, base_name + ".md")
        else:
            dir_name = os.path.dirname(output_path)
            base_name = os.path.splitext(os.path.basename(output_path))[0]

        # Set the output_files_dir in resources to specify where images will be saved
        resources["output_files_dir"] = f"{base_name}_files"

        # Perform the conversion
        body, resources = exporter.from_notebook_node(
            self.notebook, resources=resources
        )

        # Use FilesWriter to save the output and resources
        writer = FilesWriter()
        writer.build_directory = dir_name
        output_file = writer.write(body, resources, notebook_name=base_name)

        # Collect the generated files
        self.generated_files.append(output_file)  # Main output file
        # Collect resource files (e.g., images)
        output_files_dir = os.path.join(dir_name, resources["output_files_dir"])
        if "outputs" in resources:
            for filename in resources["outputs"]:
                file_path = os.path.join(output_files_dir, filename)
                self.generated_files.append(file_path)

        print(f"Markdown file saved to {output_file}")
        print(f"Resources saved to {output_files_dir}")

    def process(self):
        """Execute the full conversion process."""
        self.load_notebook()
        self.update_kernelspec()
        if self.execute:
            self.execute_notebook()

    def get_output_extension(self):
        return ".md"
