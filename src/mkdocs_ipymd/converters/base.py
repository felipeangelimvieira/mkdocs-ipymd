import os
import pathlib
from tempfile import TemporaryDirectory

__all__ = ["BaseConverter", "SequentialConverter"]

class BaseConverter:
    """
    Base class for converters.
    
    Attributes
    ----------
    VALID_INPUT_EXTENSIONS : tuple
        A tuple of valid input file extensions.
    """

    VALID_INPUT_EXTENSIONS = (None,)

    def __init__(self):
        ...

    def _validate_filepath(self, input_path : str):
        """
        Check if filepath is in self.VALID_INPUT_EXTENSIONS.
        
        Also check if file exists
        
        Parameters
        ----------
        input_path : str
            The path to the input file.
            
        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """
        input_path = str(input_path)

        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")

        if not input_path.endswith(self.VALID_INPUT_EXTENSIONS):
            raise ValueError(f"Invalid file extension: {input_path}")

    def convert(self, input_path : str, output_path : str):
        """
        Convert input_path to output_path.
        """
        self._validate_filepath(input_path)
        self._convert(input_path, output_path)

    def _convert(self, input_path : str, output_path : str):
        raise NotImplementedError("Subclasses must implement _convert method")

    def save(self, output_path : str):
        """
        Default save method calls convert with self.filepath as input.
        """
        self.convert(self.filepath, output_path)

    def __rshift__(self, other : "BaseConverter") -> "SequentialConverter":
        """
        Overload the >> operator to chain converters.
        """
        if isinstance(other, BaseConverter):
            return SequentialConverter([self, other])
        elif isinstance(other, SequentialConverter):
            return SequentialConverter([self] + other.converters)
        else:
            raise TypeError("Can only chain with another BaseConverter or SequentialConverter")


class SequentialConverter(BaseConverter):
    """
    Sequential converter that applies a series of converters in order.
    
    Parameters
    ----------
    converters : list
        A list of converters to apply in order.
    
    """
    def __init__(self, converters : list):
        self.converters = converters

    def convert(self, input_path : str, output_path : str):
        """Convert input_path to output_path using the sequence of converters.

        Args:
            input_path (str): the path to the input file
            output_path (str): the path to the output file

        Returns:
            None
        """
        with TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            for idx, converter in enumerate(self.converters):
                if idx == len(self.converters) - 1:
                    # Last converter, output to the final output_path
                    converter.convert(input_path, output_path)
                else:
                    # Intermediate converter, output to temporary file
                    temp_output_path = (
                        temp_dir / f"temp_{idx}{converter.get_output_extension()}"
                    )
                    converter.convert(input_path, temp_output_path)
                    input_path = temp_output_path


    def get_output_extension(self):
        """Return the output extension of the last converter"""
        return self.converters[-1].get_output_extension()
    
    @property
    def VALID_INPUT_EXTENSIONS(self):
        return self.converters[0].VALID_INPUT_EXTENSIONS
