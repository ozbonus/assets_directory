import argparse
import json
import sys
import subprocess
from tqdm import tqdm
from collections import OrderedDict
from collections.abc import Generator
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
):
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

    Returns:
        None
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
    """Verifies an image file meets requirements for cover art.

    This function checks the following criteria for the provided image file: a
    valid image format as defined by Pillow and minimum resolution of 1000
    pixels horizontally and vertically.

    Args:
        file: The path to the image file, as a string or Path object.

    Raises:
        OSError: If the file cannot be opened as an image (e.g., corrupted file,
        not a valid image format).
        ValueError: If the image resolution is below 1000 pixels.

    Returns:
        None
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
    """Verifies an image file meets requirements for cover art.

    This function checks the following criteria for the provided image file: a
    valid image format as defined by Pillow, a minimum resolution of 1000
    pixels horizontally and vertically, and a perfectly square aspect ratio.

    Args:
        file: The path to the image file, as a string or Path object.

    Raises:
        OSError: If the file cannot be opened as an image (e.g., corrupted file,
        not a valid image format).
        ValueError: If the image resolution is below 1000 pixels.
        ValueError: If the image is not perfectly square (width != height).

    Returns:
        None
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


def verify_audio(file: Path | str):
    """Verifies that an audio file contains required metadata tags.

    This function uses TinyTag to extract metadata from an audio file and
    checks if all required tags (filename, title, album, artist, disc,
    disc_total, track, track_total, and duration) are present.

    Args:
        file: The path to the audio file, as a string or Path object.

    Raises:
        ValueError: If any of the required metadata tags are missing
            (i.e., evaluate to a falsy value like None, empty string, or 0).
        FileNotFoundError: If the provided file does not exist.

    Returns:
        None.
    """
    tag = TinyTag.get(file)
    required_tags = [
        tag.filename,
        tag.title,
        tag.album,
        tag.artist,
        tag.disc,
        tag.disc_total,
        tag.track,
        tag.track_total,
        tag.duration,
    ]
    if not all(required_tags):
        raise ValueError(f"{tag.filename} is missing required metadata.")


def verify_all_audio(files: Generator[Path | str] | list[Path | str]):
    """Verify audio files have required metadata and report how many do not.

    Args:
        files: A collection of audio files as either Path objects or string,
        contained within a either a generator or a list.

    Raises:
        ValueError: If any files are missing required metadata tags.

    Returns:
        None
    """

    invalid_files = 0

    for file in files:
        try:
            verify_audio(file)
        except ValueError:
            invalid_files += 1

    if invalid_files:
        raise ValueError(f"{invalid_files} file(s) missing required tags.")


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


def extract_metadata(path: Path) -> dict[str, str | int]:
    """Extract metadata from one audio file.

    Args:
        path: A Path object that leads to an audio file.

    Returns:
        A dictionary in a format consumable by Kantan Player apps.

    Raises:
        None. Before reaching this function an audio will have already bee
        verified to contain all of the required metadata.
    """
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


def extract_all_metadata(files: list[Path]) -> OrderedDict:
    """Extract metadata from a list of audio files.

    Args:
        list: A list of Path objects to audio files.

    Raises:
        None

    Returns:
        An OrderedDict. Every key is a filename stem of on of the audio files
        and the values are meta as created by the `extract_metadata` function.
    """
    tracks_data = OrderedDict()
    for file in tqdm(files):
        filename = file.stem
        data = extract_metadata(file)
        tracks_data[filename] = data
    return tracks_data


if __name__ == "__main__":
    args = parser.parse_args()
    verify_args(args)
    verify_ffmpeg()
    print_work_order()
