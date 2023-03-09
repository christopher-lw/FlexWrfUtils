import pytest

import xarray as xr
import numpy as np
import pint

from flexwrfutils.flexwrfoutput import (
    combine,
    FlexwrfOutput,
    get_flexpart_directories,
    set_times_to_start,
    parse_units_to_pint,
)


@pytest.fixture
def flxout():
    times = np.array(
        [b"20210802_150000", b"20210802_140000", b"20210802_130000"], dtype="|S15"
    )

    flxout = xr.Dataset(
        data_vars=dict(
            Times=(["Time"], times),
            CONC=(
                [
                    "Time",
                    "ageclass",
                    "releases",
                    "bottom_top",
                    "south_north",
                    "west_east",
                ],
                np.ones((3, 1, 2, 2, 4, 5)),
            ),
        )
    )
    return flxout


@pytest.fixture
def header():
    header = xr.Dataset(
        data_vars=dict(
            XLONG_CORNER=(["south_north", "west_east"], np.ones((4, 5))),
            XLAT_CORNER=(["south_north", "west_east"], np.ones((4, 5))),
            ZTOP=(["bottom_top"], np.ones(2)),
            SPECIES=(["species"], np.ones(1)),
            AGECLASS=(["ageclass"], np.ones(1)),
            Times=(["Time"], []),
            ReleaseName=(["releases"], np.ones(2).astype(str)),
            ReleaseTstart_end=(["releases", "ReleaseStartEnd"], np.ones((2, 2))),
            ReleaseXstart_end=(["releases", "ReleaseStartEnd"], np.ones((2, 2))),
            ReleaseYstart_end=(["releases", "ReleaseStartEnd"], np.ones((2, 2))),
            ReleaseZstart_end=(["releases", "ReleaseStartEnd"], np.ones((2, 2))),
            ReleaseNP=(["releases"], np.ones(2)),
            ReleaseXMass=(["releases", "species"], np.ones((2, 1))),
            ReceptorLon=(["receptors"], []),
            ReceptorLat=(["receptors"], []),
            ReceptorName=(["receptors"], []),
            TOPOGRAPHY=(["south_north", "west_east"], np.ones((4, 5))),
            GRIDAREA=(["south_north", "west_east"], np.ones((4, 5))),
        ),
        coords=dict(
            XLONG=(["south_north", "west_east"], np.arange(4 * 5).reshape((4, 5))),
            XLAT=(["south_north", "west_east"], np.arange(4 * 5).reshape((4, 5))),
        ),
    )
    return header


@pytest.fixture
def simple_flexwrf_output(flxout, header):
    flexwrf_output = FlexwrfOutput(flxout, header)
    return flexwrf_output


def test_combine(flxout, header):
    combination = combine(flxout, header)
    assert "CONC" in combination.data_vars
    assert "XLONG" in combination.coords


def test_get_flexpart_directories(tmp_path):
    content = "content"

    parent_directory = tmp_path / "parent"
    parent_directory.mkdir()
    flexpart_dirs = [parent_directory / f"dir{i}" for i in range(2)]
    [flexpart_dir.mkdir() for flexpart_dir in flexpart_dirs]
    [
        (flexpart_dir / "flexwrf.input").write_text(content)
        for flexpart_dir in flexpart_dirs
    ]

    other_dir = parent_directory / "other"
    other_dir.mkdir()

    flexpart_dirs_func = get_flexpart_directories([parent_directory])
    assert set(flexpart_dirs) == set(flexpart_dirs_func)
    assert other_dir not in flexpart_dirs_func


def test_set_times_to_start(simple_flexwrf_output):
    changed_data = set_times_to_start(simple_flexwrf_output.data)
    assert changed_data == simple_flexwrf_output.data.sortby(
        "Time"
    ).Time - np.datetime64(1, "h")


def test_parse_units_to_pint():
    units = "m s3 kg-1"
    assert parse_units_to_pint(units) == pint.Unit("m*s^3*kg^-1")


class Test_FlexwrfOutput:
    def test_longitudes(self, simple_flexwrf_output):
        assert simple_flexwrf_output.longitudes is not None

    def test_latitudes(self, simple_flexwrf_output):
        assert simple_flexwrf_output.latitudes is not None

    def test_total(self, simple_flexwrf_output):
        assert len(simple_flexwrf_output.total.dims) == 2
        assert simple_flexwrf_output.total.values[0][0] == 12

    def test_isel(self, simple_flexwrf_output):
        selected_output = simple_flexwrf_output.isel(releases=0)
        assert selected_output.data == simple_flexwrf_output.data.isel(releases=0)

    def test_sum_non_spatial(self, simple_flexwrf_output):
        summed_data = FlexwrfOutput.sum_non_spatial(
            simple_flexwrf_output.isel(releases=0).data.CONC
        )
        assert len(summed_data.dims) == 2

    def test_extent(self, simple_flexwrf_output):
        extent = simple_flexwrf_output.extent
        assert extent[0] == simple_flexwrf_output.data.XLONG_CORNER.min()
        assert extent[1] == simple_flexwrf_output.data.XLONG_CORNER.max()
        assert extent[2] == simple_flexwrf_output.data.XLAT_CORNER.min()
        assert extent[3] == simple_flexwrf_output.data.XLAT_CORNER.max()

    def test_concentrations(self, simple_flexwrf_output):
        concentrations = simple_flexwrf_output.formatted_concentrations
        assert (
            simple_flexwrf_output.data.CONC.squeeze(drop=True).values
            == concentrations.values
        ).all()

    def test_simulation_start(self, simple_flexwrf_output):
        assert simple_flexwrf_output.simulation_start == np.datetime64(
            "2021-08-02T15:00:00"
        )

    def test_release_starts(self, simple_flexwrf_output):
        release_starts = simple_flexwrf_output.release_starts
        expected_release_start = (
            simple_flexwrf_output.simulation_start
            + simple_flexwrf_output.data.ReleaseTstart_end.isel(
                ReleaseStartEnd=0
            ).astype("timedelta64[s]")
        )
        assert (release_starts == expected_release_start).all()
