import numpy as np
import pandas as pd
import pytest
import xarray as xr

from flexwrfutils.scripts.make_AVAILABLE import (
    assign_files,
    convert_to_datetime64,
    extract_datetime_strings,
    update_file_index,
)


@pytest.fixture
def timerange_info():
    return pd.DataFrame(
        dict(
            file_path=["file1", "file2"],
            min=[
                np.datetime64("2009-01-01T00:00:00"),
                np.datetime64("2010-01-01T00:00:00"),
            ],
            max=[
                np.datetime64("2010-01-01T00:00:00"),
                np.datetime64("2011-01-01T00:00:00"),
            ],
        )
    )


def test_convert_to_datetime64():
    binary_times = xr.DataArray([b"2000-01-01_01:01:01", b"2000-01-01_01:01:02"])
    datetime64_times = convert_to_datetime64(binary_times)
    assert isinstance(
        datetime64_times, np.ndarray
    ), f"Wrong output type. Should be np.ndarray but is {type(datetime64_times)}"


@pytest.mark.parametrize(
    "time,start_input_index,start_output_index,end_input_index,end_output_index",
    [
        (np.datetime64("2009-01-01T00:00:00"), 0, 0, 0, 0),
        (np.datetime64("2010-01-01T00:00:00"), 0, 1, 0, 0),
        (np.datetime64("2011-01-01T00:00:00"), 1, 1, 0, 1),
    ],
)
def test_update_file_index(
    time,
    timerange_info,
    start_input_index,
    start_output_index,
    end_input_index,
    end_output_index,
):
    calculated_output_index = update_file_index(
        time, start_input_index, timerange_info, overlap_choice="start"
    )
    assert calculated_output_index == start_output_index

    calculated_output_index = update_file_index(
        time, end_input_index, timerange_info, overlap_choice="end"
    )
    assert calculated_output_index == end_output_index


def test_assign_files(timerange_info):
    times = np.array(
        [
            np.datetime64("2009-01-01T00:00:00"),
            np.datetime64("2010-01-01T00:00:00"),
            np.datetime64("2011-01-01T00:00:00"),
        ]
    )
    assert assign_files(times, timerange_info, "start") == ["file1", "file2", "file2"]
    assert assign_files(times, timerange_info, "end") == ["file1", "file1", "file2"]


def test_extract_datetime_strings():
    wrf_times = np.array([np.datetime64("2009-01-01T00:00:00")])
    dates, times = extract_datetime_strings(wrf_times)
    assert len(dates) == len(times) == len(wrf_times)
    assert (
        len(dates[0]) == 8
    ), f"Date string do not have correct lenghts (got {len(dates[0])} instead of 8)"
    assert (
        len(times[0]) == 6
    ), f"Time string do not have correct lenghts (got {len(times[0])} instead of 6)"
