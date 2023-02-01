from flexwrfutils.classes.flexwrfinput import FlexWrfOption
from flexwrfutils.classes.flexwrfenum import (
    PathnamesArgs,
    CommandArgs,
    AgeclassheaderArgs,
    AgeclassinstanceArgs,
    OutgridArgs,
    OutgridnestArgs,
    OutgridlevelArgs,
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


# TESTS FlexWrfOption
@pytest.fixture
def file_content():
    example_path = Path(__file__).parent / "file_examples" / "flexwrf.input.forward1"
    with open(example_path, "r") as f:
        file_content = f.readlines()
    return file_content


@pytest.mark.parametrize(
    "OptionEnum,start_index,end_index",
    [
        (PathnamesArgs, 0, 5),
        (CommandArgs, 5, 41),
        (AgeclassheaderArgs, 41, 43),
        (AgeclassinstanceArgs, 43, 44),
        (OutgridArgs, 45, 54),
        (OutgridlevelArgs, 54, 55),
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
