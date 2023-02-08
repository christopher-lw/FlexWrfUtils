import argparse


def get_parser():
    parser = argparse.ArgumentParser(
        description="Script to insert coordinates (times and positions) of releases from textfile into flexwrf.input file."
    )
    parser.add_argument(
        "coordinate_file", type=str, help="Path to file with coordinate information."
    )
    parser.add_argument(
        "flexwrf_input_file", type=str, help="Path to flexwrf.input file to insert in."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Directory to which modified flexwrf.input file is saved to. If None, the directory of flexwrf_input_file is chosen.",
    )
    parser.add_argument(
        "--output_name",
        type=str,
        default=None,
        help="Name for output file. If None, an automaitc name is chosen.",
    )
    return parser


def main():
    raise NotImplementedError


if __name__ == "__main__":
    main()
