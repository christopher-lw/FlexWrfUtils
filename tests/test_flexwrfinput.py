from flexwrfutils.classes.flexwrfinput import FlexWrfOption, FlexWrfInput
from flexwrfutils.classes.flexwrfenum import (
    PathnamesArgs,
    CommandArgs,
    AgeclassheaderArgs,
    AgeclassinstanceArgs,
    OutgridheaderArgs,
    OutgridnestArgs,
    OutgridinstanceArgs,
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
import pytest
from pathlib import Path


@pytest.fixture
def file_content():
    example_path = Path(__file__).parent / "file_examples" / "flexwrf.input.forward1"
    with open(example_path, "r") as f:
        file_content = f.readlines()
    return file_content


##############################
#### TESTS FlexWrfOption #####
##############################


@pytest.mark.parametrize(
    "OptionEnum,start_index,end_index",
    [
        (PathnamesArgs, 0, 5),
        (CommandArgs, 5, 41),
        (AgeclassheaderArgs, 41, 43),
        (AgeclassinstanceArgs, 43, 44),
        (OutgridheaderArgs, 45, 54),
        (OutgridinstanceArgs, 54, 55),
        (OutgridnestArgs, 57, 65),
        (ReceptorheaderArgs, 65, 67),
        (SpeciesheaderArgs, 67, 70),
        (SpeciesinstanceArgs, 70, 71),
        (ReleasesheaderArgs, 72, 75),
        (ReleaseslinkArgs, 75, 76),
        (ReleasesnumpointArgs, 77, 78),
        (ReleasesinstanceArgs, 78, 88),
        (ReleasesinstancexmassArgs, 88, 89),
        (ReleasesinstancenameArgs, 90, 91),
    ],
)
class Test_FlexWrfOption_init:
    def test_init_correct(self, file_content, OptionEnum, start_index, end_index):
        option_content = file_content[start_index:end_index]
        FlexWrfOption(option_content, OptionEnum)

    @pytest.mark.xfail
    def test_init_not_correct(self, file_content, OptionEnum, start_index, end_index):
        option_content = file_content[start_index:end_index]
        option_content.append("Wrong additional line")
        FlexWrfOption(option_content, OptionEnum)


##############################
#### TESTS FlexWrfInput #####
##############################


def test_read_command_correct(file_content):
    instance = FlexWrfInput(file_content)
    instance.read_command(line_index=5)


@pytest.mark.xfail
def test_read_command_not_correct1(file_content):
    file_content.insert(6, "impostor line")
    instance = FlexWrfInput(file_content)
    instance.read_command(line_index=5)


@pytest.mark.xfail
def test_read_command_not_correct2(file_content):
    instance = FlexWrfInput(file_content)
    instance.read_command(line_index=6)


def test_read_ageclass_correct(file_content):
    instance = FlexWrfInput(file_content)
    instance.read_ageclass(line_index=41)


@pytest.mark.xfail
def test_read_ageclass_not_correct1(file_content):
    file_content.insert(43, "impostor line")
    instance = FlexWrfInput(file_content)
    instance.read_ageclass(line_index=41)


@pytest.mark.xfail
def test_read_ageclass_not_correct2(file_content):
    instance = FlexWrfInput(file_content)
    instance.read_ageclass(line_index=42)


def test_read_outgrid_correct(file_content):
    instance = FlexWrfInput(file_content)
    instance.read_outgrid(line_index=45)


@pytest.mark.xfail
def test_read_outgrid_not_correct1(file_content):
    file_content.insert(46, "impostor line")
    instance = FlexWrfInput(file_content)
    instance.read_outgrid(line_index=45)


@pytest.mark.xfail
def test_read_outgrid_not_correct2(file_content):
    instance = FlexWrfInput(file_content)
    instance.read_outgrid(line_index=46)
