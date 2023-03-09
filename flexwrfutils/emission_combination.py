"""This file contains tools to handle the combination of emissions together with the output of FLEXPART-WRF
"""
from typing import Union, List, Optional
from pathlib import Path
from copy import deepcopy

import xarray as xr
import numpy as np

from flexwrfutils import FlexwrfOutput


def decode_wrf_times(times: np.ndarray) -> np.ndarray:
    """Casts array of times in format of wrf emission input to numpy.datetime64.

    Args:
        times (np.ndarray): Numpy array of times in strings.

    Returns:
        np.ndarray: Cast times.
    """
    decoded_times = np.char.decode(times)
    decoded_times = np.char.replace(decoded_times, " ", "T")
    decoded_times = np.char.replace(decoded_times, "_", "T")
    decoded_times = decoded_times.astype(np.datetime64)
    return decoded_times


def open_emissionfile(files: Union[Path, str, List[Union[Path, str]]]) -> xr.Dataset:
    """Wrapper for xarray.open_mfdataset. Additionally, assigns coodinates.

    Args:
        files (Union[Path, str, List[Union[Path, str]]]): Files to open.

    Returns:
        xr.Dataset: Opened data with adjusted coordinates.
    """
    emissions = xr.open_mfdataset(files, concat_dim="Time", combine="nested")
    emissions = emissions.assign_coords(Time=decode_wrf_times(emissions.Times.values))
    emissions = emissions.assign_coords(
        XLAT=(["south_north", "west_east"], emissions.XLAT.isel(Time=0).values)
    )
    emissions = emissions.assign_coords(
        XLONG=(["south_north", "west_east"], emissions.XLONG.isel(Time=0).values)
    )
    return emissions


def match_coordinates(
    flexwrf_output: FlexwrfOutput, emissions: xr.Dataset
) -> xr.Dataset:
    flexwrf_data = deepcopy(flexwrf_output.data)
    for coord in ["XLONG", "XLAT"]:
        if np.allclose(flexwrf_data.coords[coord], emissions.coords[coord]):
            flexwrf_data = flexwrf_data.assign_coords({coord: emissions.coords[coord]})
        else:
            raise ValueError(
                "Spatial coordinates of the output and the emissions is not equal enough"
            )
    return flexwrf_data


def get_emission_files(
    parent_directory: Union[str, Path], emission_files: Optional[List[str]] = None
) -> List[Path]:
    parent_directory = Path(parent_directory)
    if emission_files is None:
        emission_paths = [path for path in parent_directory.iterdir()]
    else:
        emission_paths = [
            parent_directory / emission_file for emission_file in emission_files
        ]
    return emission_paths
