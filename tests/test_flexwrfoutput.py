import pytest

import xarray as xr
import numpy as np

from flexwrfutils.flexwrfoutput import combine, FlexwrfOutput


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
