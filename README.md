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
