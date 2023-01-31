import argparse
from pathlib import Path
from typing import List, Literal, Tuple

import numpy as np
import pandas as pd
import xarray as xr


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Script to construct AVAILABLE files for FLEXPART-WRF.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="wrfout_d01_",
        help="Common part of WRF output filename.",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Directory with WRF output to produce AVAILABLE file for.",
    )
    parser.add_argument(
        "--output_name",
        type=str,
        default="AVAILABLE",
        help="Name for outpt file. (Will be saved into 'directory').",
    )
    parser.add_argument(
        "--time_datavariable",
        type=str,
        default="Times",
        help="Coordinate of WRF output to read out for extracting times.",
    )
    parser.add_argument(
        "--overlap_choice",
        default="start",
        choices=["start", "end"],
        help="Determines which to which file the overlaping times are assigned to. 'start'/'end' the file that starts/ends in the overlapping interval.",
    )
    return parser


def convert_to_datetime64(wrf_times: xr.DataArray) -> np.ndarray:
    return np.char.replace(np.char.decode(wrf_times.values), "_", "T").astype(
        "datetime64[s]"
    )


def update_file_index(
    time: str,
    file_index: int,
    timerange_info: pd.DataFrame,
    overlap_choice: Literal["start", "end"],
) -> int:
    # if the last WRF file is used then keep using it till the end
    if file_index == len(timerange_info) - 1:
        return file_index

    current_maximum = timerange_info.iloc[file_index]["max"]
    next_minimum = timerange_info.iloc[file_index + 1]["min"]

    # handle cases whithout overlap
    if current_maximum < time:
        return file_index + 1
    if next_minimum > time:
        return file_index
    # in case of overlap
    # for "start" switch to next file
    if overlap_choice == "start":
        return file_index + 1
    # for "end" stay at current file
    elif overlap_choice == "end":
        return file_index
    return file_index


def assign_files(
    times: np.ndarray,
    timerange_info: pd.DataFrame,
    overlap_choice: Literal["start", "end"],
):
    file_list = []
    file_index = 0

    for time in times:
        file_index = update_file_index(time, file_index, timerange_info, overlap_choice)
        file_list.append(timerange_info.iloc[file_index]["file_path"])
    return file_list


def extract_datetime_strings(
    wrf_times: np.ndarray,
) -> Tuple[List[str], List[str]]:
    dates = []
    times = []
    wrf_times = wrf_times.astype(str)
    for wrf_time in wrf_times:
        date, time = wrf_time.replace("-", "").replace(":", "").split("T")
        dates.append(date)
        times.append(time)
    return dates, times


def main():
    parser = get_parser()
    args = parser.parse_args()

    file_directory = Path(args.directory)
    output_file = file_directory / args.output_name
    wrf_files = file_directory.glob(f"{args.filename}*")

    wrf_total_times = []
    timerange_info = dict(file_path=[], min=[], max=[])

    for wrf_file in wrf_files:
        wrf_file_times = xr.open_dataset(wrf_file)[args.time_datavariable]
        wrf_file_times = convert_to_datetime64(wrf_file_times)
        wrf_total_times.extend(wrf_file_times)
        timerange_info["file_path"].append(wrf_file)
        timerange_info["min"].append(wrf_file_times.min())
        timerange_info["max"].append(wrf_file_times.max())

    wrf_total_times = np.array(wrf_total_times).astype("datetime64[s]")
    wrf_total_times = np.unique(wrf_total_times)
    timerange_info = pd.DataFrame(timerange_info)
    timerange_info = timerange_info.sort_values(by="min")

    assigned_wrf_files = assign_files(
        wrf_total_times, timerange_info, args.overlap_choice
    )
    dates, times = extract_datetime_strings(wrf_total_times)

    with output_file.open("w") as available_file:
        available_file.write("XXXXXX EMPTY LINES XXXXXXXXX\n")
        available_file.write("XXXXXX EMPTY LINES XXXXXXXX\n")
        available_file.write(
            "YYYYMMDD HHMMSS      name of the file(up to 80 characters)\n"
        )
        for assigned_wrf_file, date, time in zip(assigned_wrf_files, dates, times):
            available_file.write(f"{date} {time}      '{assigned_wrf_file}'      ' '\n")


if __name__ == "__main__":
    main()
