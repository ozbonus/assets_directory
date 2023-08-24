# Readme

[Working with the Python virtual environment.](https://python-poetry.org/docs/basic-usage/#using-poetry-run)

You should activate the environment with `poetry shell` and make sure that the interpreter given in Ruff's settings either points to the one defined by poetry's shell or some other interpreter. You can quickly copy the path by running `which python | pbcopy` in the terminal.

## Encoding Audio

We're going with `aac` audio as implementd by `fdk-aac`. We're using the `m4a` container format because raw `aac` files don't contain the necessary headers for communicating track length. After a lot of tweaking, I've come to these encoding settings, which are written in the format that `ffmpeg-python` prefers.

```python
acodec="libfdk_aac", # Requires specially-compiled ffmpeg.
aprofile="aac_he", # Performs well at low bitrates.
vbr=0, # Disable variable bitrate.
ab="32k", # Minimum bitrate for clear speech.
ar=44100, # Sampling rate.
ac=1, # Downmix stereo to mono.
```

There is profile called `aac_he_v2`, but as I understand it only provides optimizations for stereo audio at low bitrates. In the event that we really need to preserve the stereo separation of a source audio track, we can set `aprofile="aac_he_v2` and `ac=2`.

[Fraunhofer FDK AAC on the Hydrogen Audio Wiki](https://wiki.hydrogenaud.io/index.php?title=Fraunhofer_FDK_AAC)

[AAC on Wikipedia](https://en.wikipedia.org/wiki/High-Efficiency_Advanced_Audio_Coding#Versions)

[FFMPEG's AAC Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/AAC)

[Another FDK AAC Reference](http://underpop.online.fr/f/ffmpeg/help/libfdk_005faac.htm.gz)

[ffmpeg-python API Reference](https://kkroening.github.io/ffmpeg-python/)

## Future Improvements

Not long ago, the folks at Fraunhofer released xHE-AAC, which maintains, in my opinion, perfectly adequate sound quality even at 16kbps. However the state of encoders for macOS is in a rough state at the moment, especially if you want to encode at low bitrates.

[xHE-AAC Listening Tests](https://www2.iis.fraunhofer.de/AAC/index.html)

## Preparing Files

You will need prepare a directory with three kinds of files: audio, images, and text.

The audio files are, of course, the audio files of the textbook that the app is distributing. The image files are for the cover of the physical book and the cover of physical audio media. The text files are transcripts and translations.

Although not strictly necessary, you'll find to be most convenient to have all of the files within one directory, with no subdirectories.

### Preparing Audio Files

The audio files will need to be in a format that contains tags readable by the `tiny_tag` Python package. These will typically be `.mp3` files, but publishers may provide other formats.

The follow tags need to be filled:

- title
- album
- artist (currently not used)
- comment (used for display description)
- disc (if there are multiple)
- track (relative to disc)

The files must be named in such a way that the file system can sort them into the originally intended order. It doesn't really matter what the file names are because the script will rename them, but they must permit the sorting.

### Preparing Image Files

You must provide two high quality images in any common image format. Let's `.png` as an example.

`cover.png` is the cover of the physcial book or a reasonable equivalent. It will be used in the title bar of the playlist screen. It will be downsampled to several sizes bounded by width. The precise file used by the app will have to configured in `customizations.dart`.

`art.png` is the cover of the physcial media that held the original audio or a reasonable equivalent. It will be used by the operating system for notification and lock screen controls.

### Preparing Text Files

Text files contain either a transcription or translation thereof of one audio file. They must follow a specific naming scheme which includes these parts, in this order:

1. The name of the audio file, minus the extension.
1. An underscore.
1. An ISO 639-1 language code in lower case.
    1. <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>
1. An optional dash.
1. An optional ISO 3166-1 alpha-2 country code in upper case.

#### Example

There is and audio file named `001.m4a`. It could have a transcript named `001_en.txt`, and several translations named `001_jp.txt`, `001_zh-TW.txt`, etc.

#### Structuring a Translation.

In this part we'll use the term "logical lines". It refers to a string of text that terminates in a (usually invisible) newline character `\n`. A logical line may contain an arbitrary number of sentences.

Every logical line in a translation must have corresponding logical line in the transcript. If the transcript has 99 logical lines, then every translation must have exactly that many. Empty logical lines are ignored and have no effect durring processing, so you can use as many as you find convenient.

### Summary of Preparing Files

You should a directory structure that looks like this:

```text
├── my_files
    ├── 001.m4a
    ├── 001_en.txt
    ├── 001_jp.txt
    ├── 001_zh-TW.txt
    ├── cover.png
    ├── art.png
    └── cover.png
```
