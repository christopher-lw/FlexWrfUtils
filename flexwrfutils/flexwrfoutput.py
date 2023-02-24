"""This file contains functions and classes to handle the output of FLEXPART-WRF

"""
from pathlib import Path
from typing import Union, Optional, Tuple

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import QuadMesh
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


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


def add_osm_subplot(fig: plt.Figure, zoom_level: int = 10, **kwargs) -> plt.Axes:
    request = cimgt.OSM()
    ax = fig.add_subplot(projection=request.crs, **kwargs)
    ax.add_image(request, zoom_level)
    return ax


def get_output_paths(path=Union[str, Path]) -> Tuple[Path, Path]:
    path = Path(path)
    header_files = [file for file in path.iterdir() if "header" in str(file)]
    flxout_files = [file for file in path.iterdir() if "flxout" in str(file)]

    assert (
        len(header_files) == 1
    ), f"Didn't find unique header files in {path}: {header_files}"
    assert len(flxout_files) == 1, f"Didn't find unique file in {path}: {flxout_files}"

    return flxout_files[0], header_files[0]


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

    def plot_on_osm(
        self, ax: plt.Axes, data: Optional[xr.DataArray] = None, **kwargs
    ) -> Tuple[plt.Axes, QuadMesh]:
        if data is None:
            data = self.total
        data = data.where(data > 0)
        longitudes = data.XLONG.values
        latitudes = data.XLAT.values
        xy = ax.projection.transform_points(ccrs.Geodetic(), longitudes, latitudes)
        mesh = ax.pcolormesh(xy[..., 0], xy[..., 1], data, **kwargs)
        ax.set_extent(self.extent)
        return ax, mesh

    def isel(self, *args, **kwargs):
        flxout = self._flxout.isel(*args, **kwargs)
        header = self._header.isel(*args, **kwargs)
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

    # @data.setter
    # def data(self, value: xr.Dataset):
    #     assert (
    #         np.array([value[coord].values.shape == self.data[coord].values.shape for coord in self.data.coords])
    #     ).all(), "The shapes of the coordinates of the new data does not match."

    #     assert (
    #         np.array([value[var].values.shape == self.data[var].values.shape for var in self.data.data_vars])
    #     ).all(), "The shapes of the data variables of the new data does not match."
    #     self._data = value

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


def read_output(
    flxout_path: Union[str, Path], header_path: Union[str, Path]
) -> FlexwrfOutput:
    flxout_path = Path(flxout_path)
    header_path = Path(header_path)
    flxout_data = xr.open_dataset(flxout_path)
    header_data = xr.open_dataset(header_path)
    output = FlexwrfOutput(flxout_data, header_data)
    return output
