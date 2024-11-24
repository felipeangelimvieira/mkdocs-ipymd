import os

import click

from mkdocs_ipymd.converters.to_jupyter import IPyToJupyter
from mkdocs_ipymd.converters.to_markdown import JupyterToMarkdown


@click.group()
def cli():
    """Main entry point for skcausal CLI."""
    pass

@cli.command()
@click.argument("filepath", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--template-file", required=False, type=click.Path(exists=True, dir_okay=False),
    help="Path to a custom template file to use for the conversion from .ipynb to .md."\
    "Default is None, which uses the default template."
)
@click.option("--remove_all_outputs_tag", required=False, default="remove_output")
@click.option("--remove_input_tag", required=False, default="remove_input")
@click.option("--remove_cell_tag", required=False, default="remove_cell")
def ipy2md(filepath,
           template_file=None,
           remove_all_outputs_tag="remove_output",
           remove_input_tag="remove_input",
           remove_cell_tag="remove_cell"
           ):
    """
    Convert a Jupyter notebook into a Markdown file.

    FILEPATH: Path to the input .ipynb file.
    """
    converter = IPyToJupyter() >> JupyterToMarkdown(
        execute=True,
        template_file=template_file,
        remove_all_outputs_tag=remove_all_outputs_tag,
        remove_input_tag=remove_input_tag,
        remove_cell_tag=remove_cell_tag,
    )
    
    output_path = os.path.splitext(filepath)[0] + ".md"
    
    converter.convert(filepath, output_path)

cli.add_command(ipy2md)

if __name__ == "__main__":
    cli()
