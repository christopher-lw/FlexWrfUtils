from flexwrfutils.classes.flexwrfinput2 import (
    OutputPath,
    Nageclass,
    AgeclassInstance,
)
import pytest
from pathlib import Path


@pytest.fixture
def example_path():
    example_path = Path(__file__).parent / "file_examples" / "flexwrf.input.forward1"
    return example_path


@pytest.fixture
def ageclasses(example_path):
    Nage = Nageclass()
    Ageinstance = AgeclassInstance(Nage)
    with example_path.open() as f:
        for i in range(42):
            f.readline()
        Nage.read(f)
        assert Nage.value == 2
        Ageinstance.read(f)
        assert "==" in f.readline(), "Reading did not end at the correct place"
    return Nage, Ageinstance


# @pytest.fixture
# def inputpath(example_path):
#     inputpath = InputPath(n_values=0)


####################################
##### Tests for FlexwrfArgument ####
####################################


class Test_OutputPath:
    def test_linecaster(self):
        Argument = OutputPath()
        line = "  test/path  \n"
        assert Argument.linecaster(line) == Path("test/path")

    def test_line(self, example_path):
        Argument = OutputPath()
        with example_path.open() as f:
            f.readline()
            Argument.read(f)
        assert Argument.line == "/scratch2/portfolios/BMC/stela/jbrioude/test_depo1/\n"

    def test_read(self, example_path):
        Argument = OutputPath()

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
