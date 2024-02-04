import argparse
from pathlib import Path
from typing import Optional, List, Generator

from openai import OpenAI, APIError
from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument("-k", action="store", dest="key_file", required=True)
parser.add_argument("-p", action="store", dest="prompt_file", required=True)
parser.add_argument("-d", action="store", dest="directory", required=True)


def verify_args(args) -> None:
    errors: List[str] = []

    if not Path(args.key_file).exists():
        errors.append(f"* Key file not found: {args.key_file}")
    else:
        key: str = get_key(args.key_file)
        openai_error: Optional[str] = verify_openai_key(key)
        if openai_error:
            errors.append(f"* OpenAI Error: {openai_error}")

    if not Path(args.prompt_file).exists():
        errors.append(f"* Prompt file not found: {args.prompt_file}")

    if not Path(args.directory).exists():
        errors.append(f"* Directory not found: {args.directory}")

    if Path(args.directory, Path(args.prompt_file).name).exists():
        errors.append("* Don't put the prompt file in the source directory.")

    if errors:
        print("The following errors were encountered:")
        raise SystemExit("\n".join(errors))


def get_key(path: str) -> str:
    with open(path, "r") as file:
        return file.readline().strip()


def get_prompt(path: str) -> str:
    with open(path, "r") as file:
        return file.read()


def get_transcript(path: str) -> str:
    with open(path, "r") as file:
        return file.read()


def verify_openai_key(key: str) -> Optional[str]:
    client = OpenAI(api_key=key)

    try:
        client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say fnord.",
                },
            ],
            model="gpt-4",
        )
    except APIError as e:
        return e.message


def get_transcript_file_iterable(directory: str) -> Generator:
    return Path(directory).glob("*.txt")


def request_cleanup(key: str, prompt: str, transcript: str) -> str:
    client = OpenAI(api_key=key)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": transcript,
                },
            ],
        )
    except APIError as e:
        raise SystemExit(e)

    return response.choices[0].message.content


def save_cleanup(directory: str, filename: str, contents: str) -> None:
    file_path = Path(directory, filename)
    with open(file_path, "w") as file:
        file.write(contents)


if __name__ == "__main__":
    args = parser.parse_args()
    verify_args(args)

    key: str = get_key(args.key_file)
    prompt: str = get_prompt(args.prompt_file)

    output_dir = Path(args.directory) / "output"
    output_dir.mkdir(exist_ok=True)

    transcripts = list(get_transcript_file_iterable(args.directory))

    for file in tqdm(transcripts, total=len(transcripts)):
        filename = file.name
        transcript = get_transcript(file)
        clean_up = request_cleanup(key, prompt, transcript)
        save_cleanup(directory=output_dir, filename=filename, contents=clean_up)
