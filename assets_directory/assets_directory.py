import argparse
import json
import sys
from collections import OrderedDict
from functools import reduce
from pathlib import Path

import ffmpeg
from PIL import Image, ImageFilter, UnidentifiedImageError
from tinytag import TinyTag

parser = argparse.ArgumentParser()

dir = parser.add_argument_group("Directories")
dir.add_argument("input", help="Directory of original files.")
dir.add_argument("-o", dest="output", help="Output directory. Default: Input's parent.")
dir.add_argument("-p", dest="prefix", help="Prefix to audio file names and JSON keys.", default="")

jsn = parser.add_argument_group("JSON and Images")
jsn.add_argument("-j", dest="json", action="store_true", help="Process JSON and images.")
jsn.add_argument("-f", dest="extension", help="Input audio filetype. Default: mp3", default="mp3")
jsn.add_argument("-c", dest="cover", required="-j" in sys.argv, help="Book cover image, input dir.")
jsn.add_argument("-a", dest="art", required="-j" in sys.argv, help="Square album image, input dir.")
jsn.add_argument("-d", dest="disc_object", help="Disc object name. Default: Disc", default="Disc")
jsn.add_argument("-t", dest="track_object", help="Track object name. Default: Track", default="Track")

enc = parser.add_argument_group("Transcoding Settings")
enc.add_argument("-T", dest="transcode", action="store_true", help="Transcode audio files")


def create_directories(output_dir: Path) -> None:
    pass


def verify_args():
    errors = []

    if Path(args.input).exists():
        pass
    else:
        errors.append(f"* Invalid input directory: {args.input}")

    if args.output == None:
        pass
    else:
        if Path(args.output).exists():
            pass
        else:
            errors.append(f"* Invalid output directory: {args.output}")

    if args.json:
        # TODO: Check that audio files with extension exist.

        try:
            Image.open(Path(args.input) / args.cover)
        except FileNotFoundError:
            errors.append(f"* Unable to locate cover image in input directory: {args.cover}")
        except UnidentifiedImageError:
            errors.append(f"* Cannot parse cover image: {args.cover}")
        except Exception as e:
            errors.append(f"* Unexpected: {e=}, {type(e)}=")

        try:
            image = Image.open(Path(args.input) / args.art)
            if image.width != image.height:
                errors.append("* The art image must be perfectly square.")
        except FileNotFoundError:
            errors.append(f"* Unable to locate art image in input directory: {args.art}")
        except UnidentifiedImageError:
            errors.append(f"* Cannot parse art image: {args.art}")
        except Exception as e:
            errors.append(f"* Unexpected: {e=}, {type(e)}=")

    if errors:
        print("The following errors were encountered:")
        [print(e) for e in errors]
        exit("Exiting")


def make_json():
    media_items = OrderedDict()
    audio_files = sorted(Path(args.input).glob(f"*.{args.extension}"))
    disc_total = 1
    absolute_track_number = 1
    for file in audio_files:
        name = f"{args.prefix}{absolute_track_number:03}"
        tag = TinyTag.get(file)
        media_items[name] = {
            "id": f"asset:///assets/audio/{name}.aac",
            "album": tag.album,
            "title": tag.title,
            "displayDescription": tag.comment,
            "artist": tag.artist,
            "duration": tag.duration,
            "extras": {
                "discObject": args.disc_object,
                "trackObject": args.track_object,
                "disc": tag.disc or "1",
                "discTrack": tag.track.lstrip("0"),
                "absoluteTrack": str(absolute_track_number),
                "transcripts": {},
            },
        }

        # Get transcripts.
        transcripts_dict = {}
        stem = file.stem
        transcripts = Path(args.input).glob(f"{stem}_*.txt")
        for transcript_file in transcripts:
            locale_code = transcript_file.stem.split("_")[-1]
            lines = []
            with open(transcript_file, "r", encoding="utf-8") as f:
                # lines = [line.strip() for line in f if line]
                for line in f:
                    line = line.strip()
                    if line:
                        lines.append(line)
            transcripts_dict[locale_code] = lines
        media_items[name]["extras"]["transcripts"] = transcripts_dict

        disc_total = max(disc_total, int(media_items[name]["extras"]["disc"]))
        absolute_track_number += 1

    for item in media_items:
        media_items[item]["extras"]["discTotal"] = str(disc_total)

    with open(json_dir / "media_items.json", "w", encoding="utf-8") as write_file:
        json.dump(media_items, write_file, indent=4, ensure_ascii=False)

    summary.append(f"Defined {absolute_track_number} MediaItem(s) from audio file(s).")


def make_images():
    with Image.open(input / args.cover) as cover:
        for width in [640, 512, 320, 240, 120]:
            scale_factor = width / cover.width
            height = int(cover.height * scale_factor)
            blur_radius = width // 12

            write_file = output / "assets" / "images" / f"cover_{width}_{height}.png"
            blurred_file = output / "assets" / "images" / f"cover_blurred_{width}_{height}.png"
            
            resized_cover = cover.resize((width, height), Image.Resampling.LANCZOS)
            blurred_cover = resized_cover.filter(ImageFilter.GaussianBlur(radius=blur_radius))

            resized_cover.save(write_file)
            blurred_cover.save(blurred_file)

    with Image.open(input / args.art) as art:
        for size in [640, 512, 320, 240, 120]:
            write_file = output / "assets" / "images" / f"art_{size}.png"
            art.resize((size, size), Image.Resampling.LANCZOS).save(write_file)

    summary.append("Successfully converted cover and art images.")


def transcode_audio():
    absolute_track_number = 1
    files = sorted(Path(input).glob(f"*.{args.extension}"))

    for file in files:
        name = f"{args.prefix}{absolute_track_number:03}"
        write_file = output / "assets" / "audio" / f"{name}.aac"
        (
            ffmpeg.input(str(file))
            .audio.output(
                str(write_file),
                acodec="libfdk_aac",
                profile="a",
                vbr="1",
                ac=1,
                aac_coder="he_aac_v2",
            )
            .overwrite_output()
            .run()
        )
        absolute_track_number += 1

    original_size_bytes = reduce(lambda x, y: x + y, [f.stat().st_size for f in files])
    # TODO: THIS IS CURSED!
    new_size_bytes = reduce(
        lambda x, y: x + y,
        [f.stat().st_size for f in Path(output / "assets" / "audio").glob("*.aac")],
    )
    print(original_size_bytes)
    print(new_size_bytes)


if __name__ == "__main__":
    args = parser.parse_args()
    verify_args()

    input = Path(args.input)
    output = None
    if args.output != None:
        output = Path(args.output)
    else:
        output = input.parent

    summary = []

    json_dir = Path(output / "assets" / "json")
    images_dir = Path(output / "assets" / "images")
    audio_dir = Path(output / "assets" / "audio")

    if args.json:
        json_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        make_json()
        make_images()

    if args.transcode:
        audio_dir.mkdir(parents=True, exist_ok=True)
        transcode_audio()

    print(summary)