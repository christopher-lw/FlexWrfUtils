import pytest

import numpy as np
import xarray as xr

from flexwrfutils.emission_combination import (
    decode_wrf_times,
    match_coordinates,
    get_emission_files,
)
from flexwrfutils.flexwrfoutput import FlexwrfOutput


@pytest.fixture
def wrf_times():
    times = np.array([b"2021-08-02 12:00:00", b"2021-08-02_13:00:00"], dtype="|S19")
    return times


@pytest.fixture
def flexwrf_output_only_data():
    flexwrf = FlexwrfOutput()
    flexwrf._data = xr.Dataset(
        data_vars=dict(CONC=(["Time", "south_north", "west_east"], np.ones((2, 3, 4)))),
        coords=dict(
            Time=(
                "Time",
                [
                    np.datetime64("2021-08-02T12:00:00"),
                    np.datetime64("2021-08-02T13:00:00"),
                ],
            ),
            XLONG=(["south_north", "west_east"], np.arange(1, 13).reshape(3, 4)),
            XLAT=(["south_north", "west_east"], 2 * np.arange(1, 13).reshape(3, 4)),
        ),
    )
    return flexwrf


@pytest.fixture
def emissions():
    emissions = xr.Dataset(
        data_vars=dict(
            Emissions=(["Time", "south_north", "west_east"], np.ones((2, 3, 4)))
        ),
        coords=dict(
            Time=(
                "Time",
                [
                    np.datetime64("2021-08-02T12:00:00"),
                    np.datetime64("2021-08-02T13:00:00"),
                ],
            ),
            XLONG=(["south_north", "west_east"], np.arange(1, 13).reshape(3, 4) + 1e-9),
            XLAT=(
                ["south_north", "west_east"],
                2 * np.arange(1, 13).reshape(3, 4) + 1e-9,
            ),
        ),
    )
    return emissions


@pytest.fixture
def emissions_large_shift():
    emissions = xr.Dataset(
        data_vars=dict(
            Emissions=(["Time", "south_north", "west_east"], np.ones((2, 3, 4)))
        ),
        coords=dict(
            Time=(
                "Time",
                [
                    np.datetime64("2021-08-02T12:00:00"),
                    np.datetime64("2021-08-02T13:00:00"),
                ],
            ),
            XLONG=(["south_north", "west_east"], np.arange(1, 13).reshape(3, 4) + 10),
            XLAT=(
                ["south_north", "west_east"],
                2 * np.arange(1, 13).reshape(3, 4) + 10,
            ),
        ),
    )
    return emissions


def test_decode_wrf_times(wrf_times):
    decoded_times = decode_wrf_times(wrf_times)
    assert decoded_times[0] == np.datetime64("2021-08-02T12:00:00")
    assert decoded_times[1] == np.datetime64("2021-08-02T13:00:00")


def test_match_coordinates(flexwrf_output_only_data, emissions):
    for coord in ["XLONG", "XLAT"]:
        assert (flexwrf_output_only_data.data[coord] != emissions[coord]).all()
    matched_data = match_coordinates(flexwrf_output_only_data, emissions)
    for coord in ["XLONG", "XLAT"]:
        assert (matched_data[coord] == emissions[coord]).all()


@pytest.mark.xfail
def test_match_coordinates_large_shift(flexwrf_output_only_data, emissions_large_shift):
    matched_data = match_coordinates(flexwrf_output_only_data, emissions_large_shift)
    _ = matched_data


def test_get_emission_files(tmp_path):
    content = "content"

    parent_directory = tmp_path / "emissions"
    parent_directory.mkdir()
    emission_file_names = [f"file{i}" for i in range(3)]
    emission_file_paths = [
        parent_directory / emission_file_name
        for emission_file_name in emission_file_names
    ]
    [emission_file.write_text(content) for emission_file in emission_file_paths]

    emission_file_paths_func = get_emission_files(parent_directory)
    assert set(emission_file_paths) == set(emission_file_paths_func)

    emission_file_paths_func = get_emission_files(
        parent_directory, emission_file_names[1:]
    )
    assert set(emission_file_paths[1:]) == set(emission_file_paths_func)
