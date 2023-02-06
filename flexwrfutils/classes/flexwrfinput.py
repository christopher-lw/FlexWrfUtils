from pathlib import Path
from typing import Union, List, Dict, Any, Tuple
import numpy as np
from .flexwrfenum import (
    FlexWrfEnum,
    PathnamesheaderArgs,
    PathnamesinstanceArgs,
    PathnamesfooterArgs,
    CommandArgs,
    AgeclassheaderArgs,
    AgeclassinstanceArgs,
    OutgridheaderArgs,
    OutgridinstanceArgs,
    OutgridnestArgs,
    ReceptorheaderArgs,
    SpeciesheaderArgs,
    SpeciesinstanceArgs,
    ReleasesheaderArgs,
    ReleaseslinkArgs,
    ReleasesnumpointArgs,
    ReleasesinstanceArgs,
    ReleasesinstancexmassArgs,
    ReleasesinstancenameArgs,
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


class OptionReader:
    def __init__(self, file_content: List[str], line_index: int):
        self._file_content = file_content
        self._start_line_index = line_index
        self._line_index = line_index
        self._options = []

    def read_static(self, OptionEnum: FlexWrfEnum) -> Tuple[int, FlexWrfOption]:
        expected_end = self._line_index + len(OptionEnum)
        option_content = self._file_content[self._line_index : expected_end]
        self._options.append(FlexWrfOption(option_content, OptionEnum))
        self._line_index = expected_end

    def read_flexible(
        self, OptionEnum: FlexWrfEnum, relative_specifier_position: int
    ) -> Tuple[int, List[FlexWrfOption]]:
        expected_instances = int(
            self._file_content[self._line_index + relative_specifier_position]
            .strip()
            .split(" ")[0]
        )
        for _ in range(expected_instances):
            self.read_static(OptionEnum)

    def check_start(self, OptionEnum: FlexWrfEnum):
        assert (
            "==" in self._file_content[self._line_index]
        ), f"Expected '==' at start of option section {OptionEnum.name}."

    def check_end(self, OptionEnum: FlexWrfEnum):
        assert (
            "==" in self._file_content[self._line_index]
        ), f"Expected line with '==' after end of option section {OptionEnum.name}."


class PathnamesReader(OptionReader):
    def read(self) -> Tuple[int, List[FlexWrfOption]]:
        self._options = []
        self._line_index = self._start_line_index
        self.check_start(PathnamesheaderArgs)
        self.read_static(PathnamesheaderArgs)
        while "==" not in self._file_content[self._line_index]:
            self.read_static(PathnamesinstanceArgs)
        self.read_static(PathnamesfooterArgs)
        self.check_end(PathnamesfooterArgs)
        return self._line_index, self._options


class CommandReader(OptionReader):
    def read(self) -> Tuple[int, List[FlexWrfOption]]:
        self._options = []
        self._line_index = self._start_line_index
        self.check_start(CommandArgs)
        self.read_static(CommandArgs)
        self.check_end(CommandArgs)
        return self._line_index, self._options


class AgeclassReader(OptionReader):
    def read(self) -> Tuple[int, List[FlexWrfOption]]:
        self._options = []
        self._line_index = self._start_line_index
        self.check_start(AgeclassheaderArgs)
        self.read_static(AgeclassheaderArgs)
        self.read_flexible(AgeclassinstanceArgs, -1)
        self.check_end(AgeclassinstanceArgs)
        return self._line_index, self._options


class OutgridReader(OptionReader):
    def read(self) -> Tuple[int, List[FlexWrfOption]]:
        self._options = []
        self._line_index = self._start_line_index
        self.check_start(OutgridheaderArgs)
        self.read_static(OutgridheaderArgs)
        self.read_flexible(OutgridinstanceArgs, -1)
        return self._line_index, self._options


class OutgridnestReader(OptionReader):
    def read(self) -> Tuple[int, List[FlexWrfOption]]:
        self._options = []
        self._line_index = self._start_line_index
        self.check_start(OutgridnestArgs)
        self.read_static(OutgridnestArgs)
        self.check_end(OutgridnestArgs)
        return self._line_index, self._options


class ReceptorReader(OptionReader):
    def read(self) -> Tuple[int, List[FlexWrfOption]]:
        self._options = []
        self._line_index = self._start_line_index
        self.check_start(ReceptorheaderArgs)
        self.read_static(ReceptorheaderArgs)
        self.check_end(ReceptorheaderArgs)
        return self._line_index, self._options


class SpeciesReader(OptionReader):
    def read(self) -> Tuple[int, List[FlexWrfOption]]:
        self._options = []
        self._line_index = self._start_line_index
        self.check_start(SpeciesheaderArgs)
        self.read_static(SpeciesheaderArgs)
        self.read_flexible(SpeciesinstanceArgs, -2)
        self.check_end(SpeciesinstanceArgs)
        return self._line_index, self._options


class ReleasesReader(OptionReader):
    def read(self) -> Tuple[int, List[FlexWrfOption]]:
        self._options = []
        self._line_index = self._start_line_index
        self.check_start(ReleasesheaderArgs)
        self.read_static(ReleasesheaderArgs)
        number_of_species = int(
            self._file_content[self._line_index - 2].strip().split(" ")[0]
        )
        self.read_flexible(ReleaseslinkArgs, -2)

        self.read_static(ReleasesnumpointArgs)
        number_of_releases = int(
            self._file_content[self._line_index - 1].strip().split(" ")[0]
        )
        for _ in range(number_of_releases):
            self.read_static(ReleasesinstanceArgs)
            for _ in range(number_of_species):
                self.read_static(ReleasesinstancexmassArgs)
            self.read_static(ReleasesinstancenameArgs)


class FlexWrfInput:
    def __init__(self, file_content: List[str]):
        self._file_content = file_content

    def read(self):
        reader_list = [
            PathnamesReader,
            CommandReader,
            AgeclassReader,
            OutgridReader,
            OutgridnestReader,
            ReceptorReader,
            SpeciesReader,
            ReleasesReader,
        ]
        line_index = 0
        for Reader in reader_list:
            line_index,

    def read_pathnames(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        Reader = PathnamesReader(self._file_content, line_index)
        return Reader.read()

    def read_command(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        Reader = CommandReader(self._file_content, line_index)
        return Reader.read()

    def read_ageclass(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        Reader = AgeclassReader(self._file_content, line_index)
        return Reader.read()

    def read_outgrid(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        Reader = OutgridReader(self._file_content, line_index)
        return Reader.read()

    def read_outgridnest(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        Reader = OutgridnestReader(self._file_content, line_index)
        return Reader.read()

    def read_receptor(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        Reader = ReceptorReader(self._file_content, line_index)
        return Reader.read()

    def read_species(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        Reader = SpeciesReader(self._file_content, line_index)
        return Reader.read()

    def read_releases(self, line_index: int) -> Tuple[int, List[FlexWrfOption]]:
        Reader = ReleasesReader(self._file_content, line_index)
        return Reader.read()
