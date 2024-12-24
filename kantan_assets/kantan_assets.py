import argparse
import json
import sys
import subprocess
from collections import OrderedDict
from functools import reduce
from pathlib import Path, PurePath

import ffmpeg
from PIL import Image, ImageFilter, UnidentifiedImageError
from tinytag import TinyTag

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Dir of files to process")
parser.add_argument("-o", dest="output", help="Output dir. Default: input dir")
parser.add_argument("-j", dest="json", action="store_true", help="Create tracks.json.")
parser.add_argument("-i", dest="image", action="store_true", help="Process images.")
parser.add_argument("-t", dest="trans", action="store_true", help="Transcode audio.")


def verify_args(args):
    errors: list[str] = []

    if not Path(args.input).exists():
        print("* The input directory is invalid.")
        exit("Exiting without side effects.")

    input_dir = Path(args.input)

    if args.output is None:
        pass
    elif not Path(args.output).exists():
        errors.append(f"* Invalid output directory: {args.output}")

    if not any([args.json, args.image, args.trans]):
        errors.append("* You must select at least one operation to perform.")

    if args.json and not any(input_dir.glob(".mp3")):
        errors.append("* No audio files were found.")

    if args.image:
        if not (Path(args.input) / "art.jpg").exists():
            errors.append("* art.jpg was not found in the input directory.")
        if not (Path(args.input) / "cover.jpg").exists():
            errors.append("* cover.jpg was not found in the input directory.")

    if args.trans:
        pass

    if errors:
        print("The following errors were encountered:")
        [print(e) for e in errors]
        exit("Exiting without side effects.")


def verify_ffmpeg(
    command: list[str] = ["ffmpeg", "-encoders"],
    library: str = "libfdk_aac",
) -> bool:
    """Verify the presence of ffmpeg and fdk_aac.

    First check for the presence of ffmpeg and exit with code 1 if it is not
    found. If ffmpeg is present on the system, then check for the presence of
    libfdk_aac by searching the output of `ffmpeg -encoders`, exiting with code
    1 if it is not found.

    Args:
        command: ffmpeg -encoders
        library: libfdk_aac

    Raises:
        FileNotFoundError: If ffmpeg is not found.
        ValueError: If "libfdk_aac" is not in the output of the command.
    """

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        output = process.stdout
        if library not in output:
            raise ValueError("libfdk_aac was not found, exiting.")
        return True
    except FileNotFoundError:
        raise FileNotFoundError("ffmpeg was not found, exiting.")


def verify_cover(file: Path | str):
    """Verify cover image presence and requirements.

    Args:
        file: Location of the image.

    Raises:
        OSError: If the file cannot be opened as an image.
        ValueError: If the image is too low resolution.
    """
    try:
        im = Image.open(file)
    except IOError:
        raise OSError("cover.jpg is not a valid image file.")

    min_size = 1000
    width: int = im.size[0]
    height: int = im.size[1]

    if width < min_size or height < min_size:
        raise ValueError(f"cover.jpg resolution is too low: {width}x{height}")

    im.close()


def verify_art(file: Path | str):
    """Verify cover image presence and requirements.

    Args:
        file: Location of the image.

    Raises:
        OSError: If the file cannot be opened as an image.
        ValueError: If the image is too low resolution.
        ValueError: If the art image is not perfectly square.
    """
    try:
        im = Image.open(file)
    except OSError:
        raise OSError("art.jpg is not a valid image file.")

    min_size = 1000
    width: int = im.size[0]
    height: int = im.size[1]

    if width < min_size or height < min_size:
        raise ValueError(f"art.jpg resolution is too low: {width}x{height}")

    if not width == height:
        raise ValueError(f"art.jpg is not square: {width}x{height}")

    im.close()


def print_work_order():
    input_directory = Path(args.input).absolute()
    print(f"Input directory: {input_directory}")

    if args.output is not None:
        output_directory = Path(args.output).absolute()
        print(f"Output directory: {output_directory}")
    else:
        print(f"Output directory: {input_directory}")

    print("")
    print("The following operations will be carried out:")

    if args.json:
        print("* Create tracks.json file.")

    if args.image:
        print("* Process cover and art images.")

    if args.trans:
        print("* Transcode audio file.")


def extract_metadata(path: str | Path, index: int) -> dict[str, str | int]:
    tag: TinyTag = TinyTag.get(path)

    metadata: dict[str, str | int | None] = {
        "filename": path.stem,
        "album": tag.album,
        "artist": tag.artist,
        "title": tag.title,
        "displayDescription": tag.comment,
        "duration": int(tag.duration * 1000),
        "disc": tag.disc,
        "discTotal": tag.disc_total,
        "track": tag.track,
        "trackTotal": tag.track_total,
    }

    return metadata


if __name__ == "__main__":
    args = parser.parse_args()
    verify_args(args)
    verify_ffmpeg()
    print_work_order()
