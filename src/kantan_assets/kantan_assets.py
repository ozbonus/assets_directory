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
    print_work_order()
