import pytest
from kantan_assets import verify_ffmpeg, verify_cover, verify_art, verify_audio


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
        assert verify_audio("./test_assets/audio_good.mp3") is None

    def test_audio_no_tags(self):
        with pytest.raises(ValueError):
            verify_audio("./test_assets/audio_no_tags.mp3")
    
    def test_audio_not_found(self):
        with pytest.raises(FileNotFoundError):
            verify_audio("./test_assets/not_a_real_file.mp3")