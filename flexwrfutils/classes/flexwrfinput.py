from pathlib import Path
from typing import Union, List, Dict, Any
import numpy as np
from .flexwrfenum import FlexWrfEnum


Pathlike = Union[Path, str]


class FlexWrfOption:
    """Class to hold and manipulate file contents of a FLEXPART-WRF input option such as COMMAND or RELEASES."""

    def __init__(self, _file_content: List[str], Argument_Enum: FlexWrfEnum):
        if len(_file_content) != len(Argument_Enum):
            raise ValueError(
                f"The length of the file content ({len(_file_content)}) doesn't match the lenght of the argument's enum ({Argument_Enum}) with length {len(Argument_Enum)}"
            )
        self._file_content = _file_content
        self._Argument_Enum = Argument_Enum

    @property
    def argument_positions(self) -> Dict[FlexWrfEnum, int]:
        argument_positions = dict(
            zip(self._Argument_Enum, np.arange(len(self._file_content)))
        )
        return argument_positions

    @property
    def arguments(self):
        arguments = [arg.name for arg in self._Argument_Enum]
        return arguments

    def update(self, argument: Union[str, FlexWrfEnum], value: Any):
        """Insert new value for an argument in the file content

        Args:
            argument (Union[str, FlexWrfEnum]): Specifies the argument to update.
            value (Any): Value to insert (will be cast to string).
        """
        argument = (
            self._Argument_Enum[argument] if isinstance(argument, str) else argument
        )
        line_index = self.argument_positions[argument]
        line_content = argument.value.replace("#", str(value)) + "\n"
        self._file_content[line_index] = line_content

    def __str__(self):
        output_string = ""
        for argument, line in zip(self._Argument_Enum, self._file_content):
            output_string += f"{argument.name}: {line}"
        return output_string


class FlexWrfInput:
    def __init__(self, flexwrf_input_path: Pathlike):
        self.flexwrf_input_path: Path = Path(flexwrf_input_path)
        self._file_content: List[str] = None

    def load(self) -> None:
        """Loads file content and saves raw and structured information"""
        pass
