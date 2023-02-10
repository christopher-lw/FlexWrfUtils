from pathlib import Path
from typing import Union, Optional, Tuple, Dict

import xarray as xr
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


class FlexwrfOutput:
    def __init__(
        self, flxout: Optional[xr.Dataset] = None, header: Optional[xr.Dataset] = None
    ):
        self._flxout = flxout
        self._header = header
        self._data: xr.Dataset = None

    def read(self, flxout_path: Union[str, Path], header_path: Union[str, Path]):
        self._flxout = xr.open_dataset(flxout_path)
        self._header = xr.open_dataset(flxout_path)

    def plot_sum(
        self,
        osm_zoom_level: int = 10,
        figsize: Tuple[float, float] = None,
        subplot_kw: Dict = dict(),
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes, QuadMesh]:
        request = cimgt.OSM()
        fig, ax = plt.subplots(
            figsize=figsize,
            subplot_kw=dict(projection=request.crs, **subplot_kw),
        )
        ax.add_image(request, osm_zoom_level)
        summed_footprint = (
            self.data.CONC.squeeze(drop=True)
            .isel(bottom_top=0)
            .sum(["Time", "releases"])
        )
        summed_footprint = summed_footprint.where(summed_footprint > 0)
        xy = ax.projection.transform_points(
            ccrs.Geodetic(), self.longitudes, self.latitudes
        )
        mesh = ax.pcolormesh(xy[..., 0], xy[..., 1], summed_footprint, **kwargs)
        ax.set_extent(self.extent)
        return fig, ax, mesh

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
        return self._data

    @property
    def values(self):
        return self.data.values

    @property
    def longitudes(self):
        return self.data.XLONG.values

    @property
    def latitudes(self):
        return self.data.XLAT.values
