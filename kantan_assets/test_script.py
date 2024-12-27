import pytest
from pathlib import Path
from kantan_assets import (
    verify_ffmpeg,
    verify_cover,
    verify_art,
    verify_audio,
    verify_all_audio,
    extract_metadata,
)


class TestVerifyFfmpeg:
    """
    In order for these tests to run correctly, you should actually have ffmpeg
    installed and compiled with libfdk_aac.
    """

    def test_ffmpeg_not_installed(self):
        with pytest.raises(FileNotFoundError):
            verify_ffmpeg(["not-ffmpeg"], "libfdk_aac")

    def test_libfdk_aac_not_found(self):
        with pytest.raises(ValueError):
            verify_ffmpeg(["ffmpeg", "-encoders"], "not-libfdk_aac")

    def test_ffmpeg_and_libfdk_aac_ok(self):
        assert verify_ffmpeg()


class TestVerifyCover:
    def test_cover_is_good(self):
        assert verify_cover("./test_assets/cover_good.jpg") is None

    def test_cover_is_not_image(self):
        with pytest.raises(OSError, match="not a valid image"):
            verify_cover("./test_assets/cover_malformed.jpg")

    def test_cover_too_small(self):
        with pytest.raises(ValueError, match="too low"):
            verify_cover("./test_assets/cover_too_small.jpg")


class TestVerifyArt:
    def test_art_is_good(self):
        assert verify_art("./test_assets/art_good.jpg") is None

    def test_art_is_not_image(self):
        with pytest.raises(OSError, match="not a valid image"):
            verify_art("./test_assets/art_malformed.jpg")

    def test_art_too_small(self):
        with pytest.raises(ValueError, match="too low"):
            verify_art("./test_assets/art_too_small.jpg")

    def test_art_is_not_square(self):
        with pytest.raises(ValueError, match="not square"):
            verify_art("./test_assets/art_not_square.jpg")


class TestVerifyAudio:
    def test_audio_is_good(self):
        assert verify_audio("./test_assets/audio_good_1.mp3") is None

    def test_audio_no_tags(self):
        with pytest.raises(ValueError):
            verify_audio("./test_assets/audio_no_tags.mp3")

    def test_audio_not_found(self):
        with pytest.raises(FileNotFoundError):
            verify_audio("./test_assets/not_a_real_file.mp3")


class TestVerifyAllAudio:
    def test_good_files(self):
        files = [
            "./test_assets/audio_good_1.mp3",
            "./test_assets/audio_good_2.mp3",
        ]
        assert verify_all_audio(files) is None

    def test_file_not_found_1(self):
        files = [
            "./test_assets/audio_good_1.mp3",
            "./test_assets/audio_good_2.mp3",
            "./test_assets/not_a_real_file.mp3",
        ]
        with pytest.raises(FileNotFoundError, match="1"):
            verify_all_audio(files)

    def test_file_not_found_2(self):
        files = [
            "./test_assets/audio_good_1.mp3",
            "./test_assets/audio_good_2.mp3",
            "./test_assets/not_a_real_file.mp3",
            "./test_assets/not_a_real_file.mp3",
        ]
        with pytest.raises(FileNotFoundError, match="2"):
            verify_all_audio(files)

    def test_invalid_file_1(self):
        files = [
            "./test_assets/audio_good_1.mp3",
            "./test_assets/audio_good_2.mp3",
            "./test_assets/audio_no_tags.mp3",
        ]
        with pytest.raises(ValueError, match="1"):
            verify_all_audio(files)

    def test_invalid_file_2(self):
        files = [
            "./test_assets/audio_good_1.mp3",
            "./test_assets/audio_good_2.mp3",
            "./test_assets/audio_no_tags.mp3",
            "./test_assets/audio_no_tags.mp3",
        ]
        with pytest.raises(ValueError, match="2"):
            verify_all_audio(files)


class TestExtractMetaData:
    def test_extract_metadata_1(self):
        file = Path("./test_assets/audio_good_1.mp3")
        expected: dict[str, str | int | None] = {
            "filename": "audio_good_1",
            "album": "Test Album",
            "artist": "Test Artist",
            "title": "Test Title",
            "displayDescription": "Test Comment",
            "duration": 30040,
            "disc": 1,
            "discTotal": 1,
            "track": 1,
            "trackTotal": 2,
        }
        assert extract_metadata(file) == expected

    def test_extract_metadata_2(self):
        file = Path("./test_assets/audio_good_2.mp3")
        expected: dict[str, str | int | None] = {
            "filename": "audio_good_2",
            "album": "Test Album",
            "artist": "Test Artist",
            "title": "Test Title",
            "displayDescription": "Test Comment",
            "duration": 30040,
            "disc": 1,
            "discTotal": 1,
            "track": 2,
            "trackTotal": 2,
        }
        assert extract_metadata(file) == expected

