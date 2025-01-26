# Kantan Assets

This converts audio files and images into a format consumable by Kantan Player.

## Testing

Testing is done with pytest. After activating your virtual environment simply run `pytest` at the root directory of the project. For some reason I can't get VS Code configured to run the tests on its own.

## Audio conversion

A directory of well-named and well-tagged audio files will be converted into a directory of re-encoded audio files with metadata stored in a file named `tracks.json`.

## Image conversion

A high resolution cover image named `cover.jpg` or `cover.png` and a high resolution art image named `art.jpg` or `art.png` will both be converted into multiple sizes.

## ffmpeg and codec support

To minimize the size of Kantan Player apps, audio files are transcoded with the Advanced Audio Codec (AAC) via ffmpeg and the Fraunhofer FDK AAC library (`libfdk_aac`). Because of the latter's licensing restrictions, prebuilt ffmpeg binaries do not include the library, so there are extra steps to take. To check if you already have ffmpeg installed with `libfdk_aac` run this command and check for it in the output:

```shell
ffmpeg -encoders
```

If it's not present, and you're using macOS and Homebrew, follow these steps, which are copied from <https://github.com/homebrew-ffmpeg/homebrew-ffmpeg>:

1. Uninstall and preexisting installations of ffmpeg.
1. run `brew install homebrew-ffmpeg/ffmpeg/ffmpeg --with-fdk-aac`
