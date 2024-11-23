
import os
import shutil
import tempfile
from pathlib import Path

import mkdocs
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files

# Import your converters
from mkdocs_ipymd.converters import IPyToJupyter, JupyterToMarkdown

__all__ = [
    "PyToMarkdownPlugin",
]



class PyToMarkdownPlugin(BasePlugin):
    config_scheme = (
        ("nbconvert_template", mkdocs.config.config_options.Type(str, default=None)),
    )
    
    def __init__(self):
        self.generated_files_directory = None

    def on_files(self, files, config):
        """
        Called after the files have been collected from the file system, but before any of them have been read.
        """
        self.generated_files_directory = config.site_dir
        new_files = []
        for file in iter(files):
            if file.src_path.endswith(".ipy"):
                # This is a .py file that we need to convert
                src_file_path = os.path.join(config.docs_dir, file.src_path)
                # Generate the output path in the temporary directory
                relative_path = os.path.splitext(file.src_path)[0] + ".md"
                temp_md_path = os.path.join(self.generated_files_directory, relative_path)

                # Ensure the directory exists
                os.makedirs(os.path.dirname(temp_md_path), exist_ok=True)

                # Use the converters to generate the markdown file
                converter_py_to_ipynb = IPyToJupyter()
                converter_ipynb_to_md = JupyterToMarkdown(execute=True,
                                                          template_file=self.config["nbconvert_template"])
                sequential_converter = converter_py_to_ipynb >> converter_ipynb_to_md
                sequential_converter.convert(src_file_path, temp_md_path)

                # Get all files from folder <filename>_files
                files_folder = os.path.join(self.generated_files_directory, os.path.splitext(file.src_path)[0] + "_files")
                generated_files = []
                for root, dirs, files in os.walk(files_folder):
                    generated_files.extend([os.path.join(root, f) for f in files])

                # Create a new File object for the generated markdown file
                new_file = File(
                    path=relative_path,
                    src_dir=self.generated_files_directory,
                    dest_dir=config.site_dir,
                    use_directory_urls=config.use_directory_urls,
                )

                new_files.append(new_file)

                for generated_file in generated_files:
                    relative_path = os.path.relpath(generated_file, self.generated_files_directory)
                    new_file = File(
                        path=relative_path,
                        src_dir=self.generated_files_directory,
                        dest_dir=config.site_dir,
                        use_directory_urls=config.use_directory_urls,
                    )
                    new_files.append(new_file)
                    
                

            else:
                new_files.append(file)

        # Return the modified files list
        return Files(new_files)

