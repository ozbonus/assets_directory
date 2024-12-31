import pytest
import json
from pathlib import Path
from collections import OrderedDict
from kantan_assets import (
    verify_ffmpeg,
    verify_cover,
    verify_art,
    verify_audio,
    verify_all_audio,
    extract_metadata,
    extract_all_metadata,
    make_directories,
    write_tracks_json,
)

TEST_ASSETS_DIRECTORY = Path("kantan_assets/test_assets")


def asset_path(filename: str) -> Path:
    relative_path = TEST_ASSETS_DIRECTORY / filename
    return relative_path.resolve()


cover_good = asset_path("cover_good.jpg")
cover_malformed = asset_path("cover_malformed.jpg")
cover_too_small = asset_path("cover_too_small.jpg")
art_good = asset_path("art_good.jpg")
art_malformed = asset_path("art_malformed.jpg")
art_too_small = asset_path("art_too_small.jpg")
art_not_square = asset_path("art_not_square.jpg")
audio_good_1 = asset_path("audio_good_1.mp3")
audio_good_2 = asset_path("audio_good_2.mp3")
audio_no_tags = asset_path("audio_no_tags.mp3")

assets_dir = Path(TEST_ASSETS_DIRECTORY / "assets")
images_dir = Path(TEST_ASSETS_DIRECTORY / "assets" / "images")
images_15x_dir = Path(TEST_ASSETS_DIRECTORY / "assets" / "images" / "1.5x")
images_20x_dir = Path(TEST_ASSETS_DIRECTORY / "assets" / "images" / "2.0x")
images_25x_dir = Path(TEST_ASSETS_DIRECTORY / "assets" / "images" / "2.5x")

tracks_json_file = Path(assets_dir / "tracks.json")
cover_10_file = Path(images_dir / "cover.webp")
cover_15_file = Path(images_15x_dir / "cover.webp")
cover_20_file = Path(images_20x_dir / "cover.webp")
cover_25_file = Path(images_25x_dir / "cover.webp")

test_metadata_dict = OrderedDict(
    {
        "audio_good_1": {
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
        },
        "audio_good_2": {
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
        },
    }
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
        assert verify_cover(cover_good) is None

    def test_cover_is_not_image(self):
        with pytest.raises(OSError, match="not a valid image"):
            verify_cover(cover_malformed)

    def test_cover_too_small(self):
        with pytest.raises(ValueError, match="too low"):
            verify_cover(cover_too_small)


class TestVerifyArt:
    def test_art_is_good(self):
        assert verify_art(art_good) is None

    def test_art_is_not_image(self):
        with pytest.raises(OSError, match="not a valid image"):
            verify_art(art_malformed)

    def test_art_too_small(self):
        with pytest.raises(ValueError, match="too low"):
            verify_art(art_too_small)

    def test_art_is_not_square(self):
        with pytest.raises(ValueError, match="not square"):
            verify_art(art_not_square)


class TestVerifyAudio:
    def test_audio_is_good(self):
        assert verify_audio(audio_good_1) is None

    def test_audio_no_tags(self):
        with pytest.raises(ValueError):
            verify_audio(audio_no_tags)


class TestVerifyAllAudio:
    def test_good_files(self):
        files = [audio_good_1, audio_good_2]
        assert verify_all_audio(files) is None

    def test_invalid_file_1(self):
        files = [audio_good_1, audio_good_2, audio_no_tags]
        with pytest.raises(ValueError, match="1"):
            verify_all_audio(files)

    def test_invalid_file_2(self):
        files = [audio_good_1, audio_good_2, audio_no_tags, audio_no_tags]
        with pytest.raises(ValueError, match="2"):
            verify_all_audio(files)


class TestExtractMetaData:
    def test_extract_metadata_1(self):
        file = Path(audio_good_1)
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
        file = Path(audio_good_2)
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


class TestExtractAllMetaData:
    def test_extract_all_metadata(self):
        files = [audio_good_1, audio_good_2]
        assert extract_all_metadata(files) == test_metadata_dict


class TestMakeDirectories:
    def test_make_directories(self):
        make_directories(TEST_ASSETS_DIRECTORY)
        assert assets_dir.exists()
        assert images_dir.exists()
        assert images_15x_dir.exists()
        assert images_20x_dir.exists()
        assert images_25x_dir.exists()
        images_15x_dir.rmdir()
        images_20x_dir.rmdir()
        images_25x_dir.rmdir()
        images_dir.rmdir()
        assets_dir.rmdir()


class TestWriteTracksJson:
    def test_write_tracks_json_writes_file(self):
        assets_dir.mkdir()
        write_tracks_json(test_metadata_dict, assets_dir)
        assert tracks_json_file.exists()
        tracks_json_file.unlink()
        assets_dir.rmdir()

    def test_tracks_json_matches_data(self):
        assets_dir.mkdir()
        write_tracks_json(test_metadata_dict, assets_dir)
        with open(tracks_json_file, "r") as read_file:
            loaded_data = json.load(read_file, object_pairs_hook=OrderedDict)
        assert loaded_data == test_metadata_dict
        tracks_json_file.unlink()
        assets_dir.rmdir()