from typing import TextIO, Any, List
from pathlib import Path


class BaseArgument:
    def __init__(self):
        self._type = None
        self._value = None
        self._dummyline = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def read(self, file: TextIO):
        line = file.readline()
        self.value = self.linecaster(line)

    def linecaster(self, line: str) -> Any:
        decoded_line = self._type(line.strip().split(" ")[0])
        return decoded_line


class StaticArgument(BaseArgument):
    @property
    def line(self):
        return self._dummyline.replace("#", str(self._value))


class DynamicArgument(BaseArgument):
    def __init__(self):
        super().__init__()
        self._n_values = 0
        self._value: List[self._type] = []

    def __len__(self):
        return len(self._value)

    def readline(self, file: TextIO):
        line = file.readline()
        self.append(self.linecaster(line))

    def read(self, file: TextIO, n_values):
        for i in range(n_values):
            line = file.readline()
            self.append(self.linecaster(line))

    @property
    def lines(self):
        lines = [self._dummyline.replace("#", str(value)) for value in self._value]
        return lines

    def append(self, value):
        self._value.append(value)
        self.n_values += 1

    def remove(self, index):
        self._value.remove(self.value[-1])
        self.n_values -= 1


class StaticSpecifierArgument(StaticArgument):
    def __init__(self):
        super().__init__()
        self._type = int
        self.children = []


class DynamicSpecifierArgument(BaseArgument):
    def __init__(self, specifier: StaticSpecifierArgument):
        super().__init__()
        self.specifier = specifier
        self._value: List[self._type] = []

    def __len__(self):
        return len(self._value)

    def readline(self, file: TextIO):
        line = file.readline()
        self.append(self.linecaster(line))

    def read(self, file: TextIO):
        n_values = self.specifier.value
        for i in range(n_values):
            line = file.readline()
            self._value.append(self.linecaster(line))

    @property
    def lines(self):
        lines = [self._dummyline.replace("#", str(value)) for value in self._value]
        return lines

    def append(self, value):
        self._value.append(value)
        self.specifier.value += 1

    def remove(self, index):
        self._value.remove(self.value[-1])
        self.specifier.value -= 1


#####################################
########## Actual Classes ###########
#####################################


class OutputPath(StaticArgument):
    def __init__(self):
        self._type = Path
        self._value = None
        self._dummyline = "#/\n"


class InputPath(OutputPath):
    def __init__(self, n_values: int):
        super().__init__(n_values)
        self._type = Path
        self._dummyline = "#/\n"


class Nageclass(StaticSpecifierArgument):
    def __init__(self):
        super().__init__()
        self._dummyline = (
            "    #                NAGECLASS        number of age classes\n"
        )


class AgeclassInstance(DynamicSpecifierArgument):
    def __init__(self, specifier):
        super().__init__(specifier)
        self._type = int
        self._dummyline = (
            "    #             SSSSSS  (int)    age class in SSSSS seconds\n"
        )
