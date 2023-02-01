from pathlib import Path
from typing import Union, List, Dict, Any, Tuple
import numpy as np
from .flexwrfenum import (
    FlexWrfEnum,
    CommandArgs,
    AgeclassheaderArgs,
    AgeclassinstanceArgs,
    OutgridheaderArgs,
    OutgridinstanceArgs,
)


Pathlike = Union[Path, str]


class FlexWrfOption:
    """Class to hold and manipulate file contents of a FLEXPART-WRF input option such as COMMAND or RELEASES."""

    def __init__(self, file_content: List[str], Argument_Enum: FlexWrfEnum):
        if len(file_content) != len(Argument_Enum):
            raise ValueError(
                f"The length of the file content ({len(file_content)}) doesn't match the lenght of the argument's enum ({Argument_Enum}) with length {len(Argument_Enum)}"
            )
        self._file_content = file_content
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
    def __init__(self, file_content: List[str]):
        self._file_content = file_content

    def read_command(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        # line index after content of COMMAND file
        expected_end = line_index + len(CommandArgs)
        assert (
            "==" in self._file_content[line_index]
        ), "Expected '==' at start of COMMAND file part."
        assert (
            "==" in self._file_content[expected_end]
        ), "Expected line with '==' after COMMAND file part"
        command = []
        command_content = self._file_content[line_index:expected_end]
        command.append(FlexWrfOption(command_content, CommandArgs))
        return expected_end, command

    def _line_reader(self, line_index: int, OptionEnum: FlexWrfEnum):
        expected_end = line_index + len(OptionEnum)
        option_content = self._file_content[line_index:expected_end]
        option = FlexWrfOption(option_content, OptionEnum)
        return expected_end, option

    def read_ageclass(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        expected_header_end = line_index + len(AgeclassheaderArgs)
        assert (
            "==" in self._file_content[line_index]
        ), "Expected '==' at start of AGECLASS file part."
        # get last line of header with information on number of instances to follow
        expected_instances = int(
            self._file_content[expected_header_end - 1].strip().split(" ")[0]
        )
        expected_end = expected_header_end + expected_instances * len(
            AgeclassinstanceArgs
        )
        assert (
            "==" in self._file_content[expected_end]
        ), "Expected line with '==' after AGECLASS file part"
        ageclass = []
        line_index, ageclass_option = self._line_reader(line_index, AgeclassheaderArgs)
        ageclass.append(ageclass_option)
        for _ in range(expected_instances):
            line_index, ageclass_option = self._line_reader(
                line_index, AgeclassinstanceArgs
            )
            ageclass.append(ageclass_option)
        return line_index, ageclass

    def read_outgrid(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        expected_header_end = line_index + len(OutgridheaderArgs)
        assert (
            "==" in self._file_content[line_index]
        ), "Expected '==' at start of AGECLASS file part."
        # get last line of header with information on number of instances to follow
        expected_instances = int(
            self._file_content[expected_header_end - 1].strip().split(" ")[0]
        )
        expected_end = expected_header_end + expected_instances * len(
            OutgridinstanceArgs
        )
        assert (
            "==" in self._file_content[expected_end]
        ), "Expected line with '==' after AGECLASS file part"
        outgrid = []
        line_index, outgrid_option = self._line_reader(line_index, OutgridheaderArgs)
        outgrid.append(outgrid_option)
        for _ in range(expected_instances):
            line_index, outgrid_option = self._line_reader(
                line_index, OutgridinstanceArgs
            )
            outgrid.append(outgrid_option)
        return line_index, outgrid
