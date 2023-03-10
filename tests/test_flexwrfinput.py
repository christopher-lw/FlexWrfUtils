from flexwrfutils.flexwrfinput import (
    StaticArgument,
    DynamicArgument,
    StaticSpecifierArgument,
    DynamicSpecifierArgument,
    DatetimeArgument,
    FlexwrfInput,
    SpeciesArgument,
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
    Nage = StaticSpecifierArgument(
        dummyline="    #                NAGECLASS        number of age classes\n"
    )
    Ageinstance = DynamicSpecifierArgument(
        Nage,
        type=int,
        dummyline="    #             SSSSSS  (int)    age class in SSSSS seconds\n",
    )
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
def decaytime(example_path):
    numtable = StaticSpecifierArgument(
        dummyline="     #               NUMTABLE        number of variable properties. The following lines are fixed format"
    )
    species = SpeciesArgument(numtable, "{:10.1f}", 14, 24)
    with example_path.open() as f:
        for i in range(68):
            f.readline()
        numtable.read(f)
        f.readline()
        species.read(f)
    return numtable, species


@pytest.fixture
def wetsb(example_path):
    numtable = StaticSpecifierArgument(
        dummyline="     #               NUMTABLE        number of variable properties. The following lines are fixed format"
    )
    species = SpeciesArgument(
        specifier=numtable,
        formatter="{:6.2f}",
        start_position=35,
        end_position=41,
    )
    with example_path.open() as f:
        for i in range(68):
            f.readline()
        numtable.read(f)
        f.readline()
        species.read(f)
    return numtable, species


@pytest.fixture
def flexwrfinput():
    flexwrfinput = FlexwrfInput()
    return flexwrfinput


@pytest.fixture
def flexwrfinput2():
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
        target_path = Path("/scratch2/portfolios/BMC/stela/jbrioude/test_depo1/")
        assert Argument.line == f"{target_path}/\n"

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


class Test_Species:
    def test_read_decaytime(self, decaytime):
        numtable, species = decaytime
        assert len(species) == numtable.value
        assert species.value[0] == -999.9

    def test_wetsb(self, wetsb):
        numtable, species = wetsb
        assert species.value == [None, 0.8]

    def test_as_string_wetsb(self, wetsb):
        numtable, species = wetsb
        assert species.as_strings() == ["      ", "  0.80"]


class Test_FlexwrfInput:
    def test_read_forward1(self, example_path, flexwrfinput):
        flexwrfinput.read(example_path)
        assert flexwrfinput.pathnames.outputpath.value == Path(
            "/scratch2/portfolios/BMC/stela/jbrioude/test_depo1/"
        )
        assert flexwrfinput.command.ldirect.value == 1
        assert len(flexwrfinput.ageclasses.ageclasses) == 2
        assert len(flexwrfinput.outgrid.levels) == 3
        assert flexwrfinput.outgrid_nest.numxgrid.value == 24
        assert len(flexwrfinput.receptor.receptor) == 0
        assert (
            len(flexwrfinput.species.weight) == flexwrfinput.species.numtable.value == 2
        )
        assert flexwrfinput.releases.xmass.value[1][0] == 0.5e4

    @pytest.mark.parametrize(
        "test_file",
        [
            ("flexwrf.input.backward1"),
            ("flexwrf.input.backward2"),
            ("flexwrf.input.forward1"),
            ("flexwrf.input.forward2"),
        ],
    )
    def test_read_lines(self, test_file, flexwrfinput):
        file_path = Path("tests") / "file_examples" / test_file
        flexwrfinput.read(file_path)
        with file_path.open() as f:
            lines = f.readlines()
        assert len(lines) == len(flexwrfinput.lines)

    @pytest.mark.parametrize(
        "test_file",
        [
            ("flexwrf.input.backward1"),
            ("flexwrf.input.backward2"),
            ("flexwrf.input.forward1"),
            ("flexwrf.input.forward2"),
        ],
    )
    def test_read_write(self, tmp_path, flexwrfinput, flexwrfinput2, test_file):
        file_path = Path("tests") / "file_examples" / test_file
        flexwrfinput.read(file_path)
        flexwrfinput.write(tmp_path / "test_file")
        flexwrfinput2.read(tmp_path / "test_file")
        options = [
            "pathnames",
            "command",
            "ageclasses",
            "outgrid",
            "outgrid_nest",
            "receptor",
            "species",
            "releases",
        ]
        for option in options:
            assert (
                getattr(flexwrfinput, option).lines
                == getattr(flexwrfinput2, option).lines
            )
        assert flexwrfinput.lines == flexwrfinput2.lines

    def test_set(self, example_path, flexwrfinput):
        flexwrfinput.read(example_path)
        flexwrfinput.pathnames.outputpath = "test/path"
        assert flexwrfinput.pathnames.outputpath.value == Path("test/path")

        flexwrfinput.outgrid.levels = [1, 2, 3]
        assert flexwrfinput.outgrid.levels.value == [1, 2, 3]

        new_ihour = np.ones((2, 24))
        flexwrfinput.releases.ihour = new_ihour
        assert (flexwrfinput.releases.ihour.value == new_ihour).all()

        new_start_dates = [np.datetime64("2009-01-01T01:01:01")] * 2
        flexwrfinput.releases.start = new_start_dates
        assert flexwrfinput.releases.start.value == ["20090101 010101"] * 2

    def test_getter(self, example_path, flexwrfinput):
        flexwrfinput.read(example_path)
        assert flexwrfinput.releases.start[0] == flexwrfinput.releases.start.value[0]

    def test_setter(self, example_path, flexwrfinput):
        flexwrfinput.read(example_path)
        flexwrfinput.releases.start[0] = np.datetime64("2009-01-01T01:01:01")
        assert (
            flexwrfinput.releases.start[0]
            == flexwrfinput.releases.start.value[0]
            == "20090101 010101"
        )
        flexwrfinput.releases.xpoint1[0] = 42
        assert (
            flexwrfinput.releases.xpoint1[0]
            == flexwrfinput.releases.xpoint1.value[0]
            == 42
        )
        flexwrfinput.releases.xmass[0] = [1, 2]
        assert (
            flexwrfinput.releases.xmass[0]
            == flexwrfinput.releases.xmass.value[0]
            == [1, 2]
        )

    def test_lines(self, example_path, flexwrfinput):
        flexwrfinput.read(example_path)
        with example_path.open() as f:
            lines = f.readlines()
        assert len(lines) == len(flexwrfinput.lines)
        wrong_endings = []
        for line in flexwrfinput.lines:
            if not "\n" == line[-1:]:
                wrong_endings.append(line)
        assert (
            len(wrong_endings) == 0
        ), f"No proper end of line character in lines:\n{wrong_endings}"
