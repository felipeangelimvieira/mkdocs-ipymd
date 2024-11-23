import os

import click

from mkdocs_ipymd.converters.to_jupyter import IPyToJupyter
from mkdocs_ipymd.converters.to_markdown import JupyterToMarkdown


@click.group()
def cli():
    """Main entry point for skcausal CLI."""
    pass


@click.command()
@click.argument("filepath", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--to", required=True, type=click.Choice(["jupyter", "markdown"]))
def convert(filepath, to):
    """
    Convert a Python script with VSCode-style cells into a Jupyter notebook.

    FILEPATH: Path to the input .py file.
    """
    if to == "jupyter":
        converter = IPyToJupyter()
        format = ".ipynb"

    elif to == "markdown":
        converter = JupyterToMarkdown(execute=True)
        format = ".md"

    # Get the output path
    dir_name = os.path.dirname(filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output_path = os.path.join(dir_name, base_name + format)
    
    converter.convert(filepath, output_path)
    print(f"Notebook saved to {output_path}")


cli.add_command(convert)

if __name__ == "__main__":
    cli()
