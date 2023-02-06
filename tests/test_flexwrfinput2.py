from flexwrfutils.classes.flexwrfinput2 import (
    StaticArgument,
    DynamicArgument,
    Nageclasses,
    AgeclassesInstance,
    DatetimeArgument,
    FlexwrfInput,
)
import numpy as np
from datetime import datetime
import pytest
from pathlib import Path


@pytest.fixture
def example_path():
    example_path = Path(__file__).parent / "file_examples" / "flexwrf.input.forward1"
    return example_path


@pytest.fixture
def ageclasses(example_path):
    Nage = Nageclasses()
    Ageinstance = AgeclassesInstance(Nage)
    with example_path.open() as f:
        for i in range(42):
            f.readline()
        Nage.read(f)
        assert Nage.value == 2
        Ageinstance.read(f)
        assert "==" in f.readline(), "Reading did not end at the correct place"
    return Nage, Ageinstance


@pytest.fixture
def inputpath(example_path):
    inputpath = DynamicArgument(type=Path, dummyline="#/\n")
    with example_path.open() as f:
        for i in range(2):
            f.readline()
        inputpath.readline(f)
    return inputpath


@pytest.fixture
def datetimeinstance(example_path):
    datetimeinstance = DatetimeArgument()
    with example_path.open() as f:
        for i in range(7):
            f.readline()
        datetimeinstance.read(f)
    return datetimeinstance


@pytest.fixture
def flexwrfinput():
    flexwrfinput = FlexwrfInput()
    return flexwrfinput


####################################
##### Tests for FlexwrfArgument ####
####################################


class Test_OutputPath:
    def test_linecaster(self):
        Argument = StaticArgument(type=Path, dummyline="#/\n")
        line = "  test/path  \n"
        assert Argument.linecaster(line) == Path("test/path")

    def test_line(self, example_path):
        Argument = StaticArgument(type=Path, dummyline="#/\n")
        with example_path.open() as f:
            f.readline()
            Argument.read(f)
        assert Argument.line == "/scratch2/portfolios/BMC/stela/jbrioude/test_depo1/\n"

    def test_read(self, example_path):
        Argument = StaticArgument(type=Path, dummyline="#/\n")

        with example_path.open() as f:
            f.readline()
            Argument.read(f)
            assert Argument.value == Path(
                "/scratch2/portfolios/BMC/stela/jbrioude/test_depo1/"
            )


class Test_Ageclass:
    def test_read(self, ageclasses):
        Nage, Ageinstance = ageclasses
        assert Nage.value == len(Ageinstance)
        assert Ageinstance.value[0] == 7200
        assert Ageinstance.value[1] == 999999

    def test_lines(self, ageclasses):
        Nage, Ageinstance = ageclasses
        line = Nage.line
        lines = Ageinstance.lines
        assert line == "    2                NAGECLASS        number of age classes\n"
        assert len(lines) == 2
        assert (
            lines[0]
            == "    7200             SSSSSS  (int)    age class in SSSSS seconds\n"
        )

    def test_append(self, ageclasses):
        Nage, Ageclasses = ageclasses
        Ageclasses.append(42)
        assert len(Ageclasses) == Nage.value
        assert (
            Ageclasses.lines[-1]
            == "    42             SSSSSS  (int)    age class in SSSSS seconds\n"
        )

    def test_remove(self, ageclasses):
        Nage, Ageclasses = ageclasses
        Ageclasses.remove(0)
        assert len(Ageclasses) == Nage.value


class Test_InputPath:
    def test_readline(self, inputpath):
        assert isinstance(inputpath.value, list)
        assert isinstance(inputpath.value[0], Path)
        assert len(inputpath) == 1


class Test_Datetime:
    def test_read(self, datetimeinstance):
        assert len(datetimeinstance.value) == 15

    def test_value_setter(self, datetimeinstance):
        timestring = "20200101 101010"
        timenp = np.datetime64("2020-01-01T10:10:10")
        timedt = datetime(2020, 1, 1, 10, 10, 10)
        datetimeinstance.value = timestring
        valuestr = datetimeinstance.value
        datetimeinstance.value = timenp
        valuenp = datetimeinstance.value
        datetimeinstance.value = timedt
        valuedt = datetimeinstance.value
        assert timestring == valuestr == valuenp == valuedt


class Test_FlexwrfInput:
    # @pytest.mark.xfail
    def test_read(self, example_path, flexwrfinput):
        flexwrfinput.read(example_path)
        assert flexwrfinput.pathnames.outputpath.value == Path(
            "/scratch2/portfolios/BMC/stela/jbrioude/test_depo1/"
        )
        assert flexwrfinput.command.ldirect.value == 1
        assert len(flexwrfinput.ageclasses.ageclasses) == 2

    def test_set(self, example_path, flexwrfinput):
        flexwrfinput.read(example_path)
        flexwrfinput.pathnames.outputpath = "test/path"
        assert flexwrfinput.pathnames.outputpath.value == Path("test/path")
