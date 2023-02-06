from flexwrfutils.classes.flexwrfinput import FlexWrfOption, FlexWrfInput

from flexwrfutils.classes.flexwrfenum import (
    PathnamesheaderArgs,
    PathnamesinstanceArgs,
    PathnamesfooterArgs,
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

pytest.skip(allow_module_level=True)


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
        (PathnamesheaderArgs, 0, 2),
        (PathnamesinstanceArgs, 2, 4),
        (PathnamesfooterArgs, 4, 5),
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


@pytest.mark.parametrize(
    "function, line_index",
    [
        ("read_pathnames", 0),
        ("read_command", 5),
        ("read_ageclass", 41),
        ("read_outgrid", 45),
        ("read_outgridnest", 57),
        ("read_receptor", 65),
        ("read_species", 67),
        ("read_releases", 72),
    ],
)
class Test_FlexWrfInput_read:
    def test_read_correctly(self, file_content, function, line_index):
        instance = FlexWrfInput(file_content)
        getattr(instance, function)(line_index)

    @pytest.mark.xfail
    def test_read_not_correctly1(self, file_content, function, line_index):
        file_content.insert(line_index + 1, "imposter line")
        instance = FlexWrfInput(file_content)
        getattr(instance, function)(line_index)

    @pytest.mark.xfail
    def test_read_not_correctly2(self, file_content, function, line_index):
        instance = FlexWrfInput(file_content)
        getattr(instance, function)(line_index + 1)
