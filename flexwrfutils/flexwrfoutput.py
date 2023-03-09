"""This file contains functions and classes to handle the output of FLEXPART-WRF

"""
from __future__ import annotations
from pathlib import Path
from typing import Union, Optional, Tuple, List, Any

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import QuadMesh
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import pint


def combine(flxout: xr.Dataset, header: xr.Dataset) -> xr.Dataset:
    """Combines dimensions of flxout with header to have full information of output in one xarray.

    Args:
        flxout (xr.Dataset): Loaded flxout file.
        header (xr.Dataset): Loader header file.

    Returns:
        xr.Dataset: Combined Dataset
    """
    combined = xr.merge([flxout, header.drop_dims("Time")])
    return combined


def add_osm_subplot(
    fig: plt.Figure,
    zoom_level: int = 10,
    request: str = "OSM",
    args=List[Any],
    **kwargs,
) -> plt.Axes:
    """Adds subplot with OpenStreet map to figure.

    Args:
        fig (plt.Figure): Figure to add subplot to.
        zoom_level (int, optional): Zoom level for added image. Defaults to 10.
        request (str, optional): Map type to get from cartopy.imagetiles. Defaults to "OSM".
        args (List[Any], optional): args for add_subplot. Defaults to None.

    Returns:
        plt.Axes: Newly created Axes with Map and respective projection.
    """
    args = [] if args is None else args
    request = getattr(cimgt, request)()
    ax = fig.add_subplot(*args, projection=request.crs, **kwargs)
    ax.add_image(request, zoom_level)
    return ax


def get_output_paths(path: Union[str, Path]) -> Tuple[Path, Path]:
    """Finds header and flxout files in directory and returns their paths.

    Args:
        path (Union[str, Path]): Path of output directory of FLEXPART-WRF.

    Returns:
        Tuple[Path, Path]: (flxout path, header path)
    """
    path = Path(path)
    header_files = [file for file in path.iterdir() if "header" in str(file)]
    flxout_files = [file for file in path.iterdir() if "flxout" in str(file)]

    assert (
        len(header_files) == 1
    ), f"Didn't find unique header files in {path}: {header_files}"
    assert len(flxout_files) == 1, f"Didn't find unique file in {path}: {flxout_files}"

    return flxout_files[0], header_files[0]


def get_flexpart_directories(parent_directories: List[Union[str, Path]]) -> List[Path]:
    """Finds subdirectories with flexwrf.input files in parent_directories.

    Args:
        parent_directories (List[Union[str, Path]]): Directories to search in.

    Returns:
        List[Path]: Paths of the subdirectories with flexwrf.input file
    """
    parent_directories = [Path(directory) for directory in parent_directories]
    flexpart_directories = []
    for parent_directory in parent_directories:
        for directory in parent_directory.iterdir():
            if (directory / "flexwrf.input").is_file():
                flexpart_directories.append(directory)
    return flexpart_directories


def set_times_to_start(flexwrf_data: xr.Dataset) -> xr.Dataset:
    """Takes Dataset with coordinate 'Time' and shifts it back one timestep.
    Args:
        flexwrf_data (xr.Dataset): Data to change coordinates in.

    Returns:
        xr.Dataset: Data with shifted 'Time' coordinate.
    """
    flexwrf_data = flexwrf_data.sortby("Time")
    time_differences = flexwrf_data.Time[1:].values - flexwrf_data.Time[:-1].values
    assert (
        time_differences == time_differences[0]
    ).all(), "Not all time steps are equal in size"
    time_step = time_differences[0]
    flexwrf_data = flexwrf_data.assign_coords(Time=flexwrf_data.Time - time_step)
    return flexwrf_data


def parse_units_to_pint(units: str):
    units = units.split(" ")
    parsed_units = ""
    for unit in units:
        for i, character in enumerate(unit):
            if character.isdigit() or character == "-":
                unit = unit[:i] + "^" + unit[i:]
                break
        parsed_units += unit + "*"
    parsed_units = pint.Unit(parsed_units[:-1])
    return parsed_units


class FlexwrfOutput:
    def __init__(
        self, flxout: Optional[xr.Dataset] = None, header: Optional[xr.Dataset] = None
    ):
        self._flxout = flxout
        self._header = header
        self._data: xr.Dataset = None
        self._total: xr.DataArray = None

    def read(self, flxout_path: Union[str, Path], header_path: Union[str, Path]):
        self._flxout = xr.open_dataset(flxout_path)
        self._header = xr.open_dataset(header_path)

    def prepare_for_osm_plot(
        self, ax: plt.Axes, data: xr.DataArray, projection=ccrs.Geodetic()
    ):
        data = data.where(data > 0)
        longitudes = data.XLONG.values
        latitudes = data.XLAT.values
        xy = ax.projection.transform_points(projection, longitudes, latitudes)
        x = xy[..., 0]
        y = xy[..., 1]
        values = data.values
        return x, y, values

    def plot_on_osm(
        self, ax: plt.Axes, data: Optional[xr.DataArray] = None, **kwargs
    ) -> Tuple[plt.Axes, QuadMesh]:
        if data is None:
            data = self.total
        x, y, values = self.prepare_for_osm_plot(ax, data)
        mesh = ax.pcolormesh(x, y, values, **kwargs)
        ax.set_extent(self.extent)
        return ax, mesh

    def isel(self, *args, **kwargs) -> FlexwrfOutput:
        flxout = self._flxout.isel(*args, **kwargs)
        header = self._header.isel(*args, **kwargs)
        return FlexwrfOutput(flxout, header)

    def sel(self, *args, **kwargs) -> FlexwrfOutput:
        flxout = self._flxout.sel(*args, **kwargs)
        header = self._header.sel(*args, **kwargs)
        return FlexwrfOutput(flxout, header)

    @staticmethod
    def sum_non_spatial(xarr: xr.DataArray):
        summable_dimenions = [
            dim for dim in xarr.dims if dim not in ["south_north", "west_east"]
        ]
        xarr_summed = xarr.sum(summable_dimenions).squeeze(drop=True)
        return xarr_summed

    @property
    def extent(self):
        lonleft = self.data.XLONG_CORNER.min()
        lonright = self.data.XLONG_CORNER.max()
        latlower = self.data.XLAT_CORNER.min()
        latupper = self.data.XLAT_CORNER.max()
        return [lonleft, lonright, latlower, latupper]

    @property
    def data(self):
        if self._data is None:
            self._data = combine(self._flxout, self._header)
            self._data = self._data.assign_coords(Time=self.times)
        return self._data

    @property
    def surface_layer_height(self) -> np.ndarray:
        return self.data.ZTOP.values

    @property
    def total(self):
        if self._total is None:
            summable_dimenions = [
                dim
                for dim in self.data.CONC.dims
                if dim not in ["south_north", "west_east"]
            ]
            self._total = self.data.CONC.sum(summable_dimenions).squeeze(drop=True)
        return self._total

    @property
    def values(self):
        return self.data.values

    @property
    def longitudes(self):
        return self.data.XLONG.values

    @property
    def latitudes(self):
        return self.data.XLAT.values

    @property
    def times(self):
        time_strings = np.char.decode(self._flxout.Times.values)
        datetime_strings = np.char.split(time_strings, "_")
        datetimes = np.array(
            [
                np.datetime64(
                    f"{t[0][:4]}-{t[0][4:6]}-{t[0][6:]}T{t[1][:2]}:{t[1][2:4]}:{t[1][4:]}"
                )
                for t in datetime_strings
            ]
        )
        return datetimes

    @property
    def formatted_concentrations(self) -> xr.DataArray:
        concentrations = self.data.CONC
        concentrations = concentrations.assign_coords(Time=self.times)
        concentrations = concentrations.rename(Time="time")
        concentrations = concentrations.squeeze(drop=True)
        concentrations = concentrations.drop(["XLONG", "XLAT"]).assign_coords(
            dict(
                latitude=(["south_north"], self.latitudes[:, 0]),
                longitude=(["west_east"], self.longitudes[0]),
            )
        )
        return concentrations

    @property
    def release_starts(self) -> xr.DataArray:
        release_starts = self.simulation_start + self.data.ReleaseTstart_end.isel(
            ReleaseStartEnd=0
        ).astype("timedelta64[s]")
        return release_starts

    @property
    def simulation_start(self) -> np.datetime64:
        return self.data.Time.max().values


def read_output(
    flxout_path: Union[str, Path], header_path: Union[str, Path]
) -> FlexwrfOutput:
    flxout_path = Path(flxout_path)
    header_path = Path(header_path)
    flxout_data = xr.open_dataset(flxout_path)
    header_data = xr.open_dataset(header_path)
    output = FlexwrfOutput(flxout_data, header_data)
    return output
