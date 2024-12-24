import pytest
from kantan_assets import verify_ffmpeg

class TestVerifyFfmpeg:
    def test_ffmpeg_not_installed(self):
        with pytest.raises(FileNotFoundError):
            verify_ffmpeg(["not-ffmpeg"], "libfdk_aac")
    
    def test_libfdk_aac_not_found(self):
        with pytest.raises(SystemExit):
            verify_ffmpeg(["ffmpeg", "-encoders"], "not-libfdk_aac")
