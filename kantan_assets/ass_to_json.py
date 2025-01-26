import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("file", help=".ass file to be converted")


def verify_file(args):
    file_path = Path(args.file)
    if not file_path.exists():
        raise OSError(f"The file '{file_path}' was not found.")


def timecode_to_milliseconds(timecode: str) -> int:
    hours, minutes, seconds_milliseconds = timecode.split(":")
    seconds, milliseconds = seconds_milliseconds.split(".")
    ms_hours = int(hours) * 3_600_000
    ms_minutes = int(minutes) * 60_000
    ms_seconds = int(seconds) * 1_000
    return ms_hours + ms_minutes + ms_seconds + int(milliseconds)


def assemble_text(chunks: list[str]) -> str:
    return ",".join(chunks).replace("\n", "")


def extract_lines(path: Path) -> dict[list[dict[str | int]]]:
    dialog_lines = {"lines": []}
    with open(path, "r") as file:
        lines = file.readlines()

    data_index = 0
    for i, line in enumerate(lines):
        if line.startswith("Format: Layer"):
            data_index = i + 1
            break

    for line in lines[data_index:]:
        chunks = line.split(",")
        start_time = timecode_to_milliseconds(chunks[1])
        end_time = timecode_to_milliseconds(chunks[2])
        speaker = chunks[4] if chunks[4] else None
        text = assemble_text(chunks[9:])
        dialog_lines["lines"].append(
            {
                "startTime": start_time,
                "endTime": end_time,
                "speaker": speaker,
                "text": text,
            }
        )

    return dialog_lines


def write_json(file_path: Path, data: dict):
    with open(file_path, "w", encoding="utf-8") as write_file:
        json.dump(data, write_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    args = parser.parse_args()
    verify_file(args)

    input_file = Path(args.file)
    output_file = input_file.with_suffix(".json")

    write_json(
        output_file,
        extract_lines(input_file),
    )
