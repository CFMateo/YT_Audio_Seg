import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import q2
import q3


class PipelineTests(unittest.TestCase):
    def test_download_skips_existing_mp3(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_stem = Path(tmpdir) / "sample"
            output_stem.with_suffix(".mp3").write_bytes(b"existing")

            with patch.object(q2.youtube_dl, "YoutubeDL") as downloader:
                q2.download_audio("video-id", str(output_stem))

            downloader.assert_not_called()

    def test_download_rejects_missing_cookie_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_stem = Path(tmpdir) / "sample"
            missing_cookie = Path(tmpdir) / "missing-cookies.txt"

            with self.assertRaises(FileNotFoundError):
                q2.download_audio(
                    "video-id",
                    str(output_stem),
                    cookiefile=str(missing_cookie),
                )

    def test_download_passes_external_cookie_to_yt_dlp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            output_stem = tmp_path / "sample"
            cookie_path = tmp_path / "external-cookies.txt"
            cookie_path.write_text("test-only", encoding="utf-8")

            with patch.object(q2.youtube_dl, "YoutubeDL") as downloader:
                q2.download_audio(
                    "video-id",
                    str(output_stem),
                    cookiefile=str(cookie_path),
                )

            options = downloader.call_args.args[0]
            self.assertEqual(options["cookiefile"], str(cookie_path))
            downloader.return_value.__enter__.return_value.download.assert_called_once()

    def test_pipeline_generates_expected_paths_without_network(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            csv_path = tmp_path / "segments.csv"
            cookie_path = tmp_path / "external-cookies.txt"
            cookie_path.write_text("test-only", encoding="utf-8")
            pd.DataFrame(
                [
                    {
                        "YTID": "sample-id",
                        "start_seconds": 1.0,
                        "end_seconds": 3.0,
                        "label_names": "Cough|Speech",
                    }
                ]
            ).to_csv(csv_path, index=False)

            def fake_download(_ytid, path, cookiefile=None):
                self.assertEqual(cookiefile, str(cookie_path))
                Path(f"{path}.mp3").write_bytes(b"raw")

            def fake_cut(_input_path, output_path, _start, _end):
                Path(output_path).write_bytes(b"cut")

            previous_cwd = os.getcwd()
            os.chdir(tmp_path)
            try:
                with patch.object(
                    q3, "download_audio", side_effect=fake_download
                ) as download_mock, patch.object(
                    q3, "cut_audio", side_effect=fake_cut
                ) as cut_mock:
                    q3.data_pipeline(
                        str(csv_path), "Cough", cookiefile=str(cookie_path)
                    )
                    q3.rename_files("audio/Cough_cut", str(csv_path))
                    q3.data_pipeline(
                        str(csv_path), "Cough", cookiefile=str(cookie_path)
                    )
            finally:
                os.chdir(previous_cwd)

            self.assertTrue((tmp_path / "audio/Cough_raw/sample-id.mp3").is_file())
            self.assertTrue(
                (tmp_path / "audio/Cough_cut/sample-id_1_3_2.mp3").is_file()
            )
            self.assertEqual(download_mock.call_count, 1)
            self.assertEqual(cut_mock.call_count, 1)

    def test_pipeline_does_not_cut_after_failed_download(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            csv_path = tmp_path / "segments.csv"
            pd.DataFrame(
                [
                    {
                        "YTID": "missing-id",
                        "start_seconds": 0.0,
                        "end_seconds": 2.0,
                        "label_names": "Cough",
                    }
                ]
            ).to_csv(csv_path, index=False)

            previous_cwd = os.getcwd()
            os.chdir(tmp_path)
            try:
                with patch.object(q3, "download_audio") as download_mock, patch.object(
                    q3, "cut_audio"
                ) as cut_mock:
                    q3.data_pipeline(str(csv_path), "Cough")
            finally:
                os.chdir(previous_cwd)

            download_mock.assert_called_once()
            cut_mock.assert_not_called()

    def test_pipeline_rejects_missing_cookie_before_processing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            csv_path = tmp_path / "segments.csv"
            pd.DataFrame(
                [
                    {
                        "YTID": "sample-id",
                        "start_seconds": 0.0,
                        "end_seconds": 2.0,
                        "label_names": "Cough",
                    }
                ]
            ).to_csv(csv_path, index=False)

            with self.assertRaises(FileNotFoundError):
                q3.data_pipeline(
                    str(csv_path),
                    "Cough",
                    cookiefile=str(tmp_path / "missing-cookies.txt"),
                )


if __name__ == "__main__":
    unittest.main()
