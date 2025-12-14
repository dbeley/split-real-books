import subprocess
from pathlib import Path

import pytest


@pytest.mark.characterization
class TestCLIHelp:
    def test_help_flag(self, split_module):
        result = subprocess.run(
            ["python3", "split-real-books.py", "--help"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Split real books into individual files" in result.stdout
        assert "--debug" in result.stdout
        assert "--config_file" in result.stdout
        assert "--compile-directory" in result.stdout
        assert "--compress" in result.stdout


@pytest.mark.characterization
class TestCLISplitMode:
    def test_split_with_valid_config(
        self, sample_config_yaml, sample_pdf, temp_dir, split_module
    ):
        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "-c", str(sample_config_yaml)]
            split_module.main()

            output_dir = temp_dir / "output"
            assert (output_dir / "Song 1 (TEST).pdf").exists()
            assert (output_dir / "Song 2 (TEST).pdf").exists()
            assert (output_dir / "Song 3 (TEST).pdf").exists()
        finally:
            sys.argv = old_argv

    def test_split_with_nonexistent_config(self, temp_dir, split_module):
        """Current behavior: raises UnboundLocalError (documented bug)."""
        import sys

        old_argv = sys.argv

        try:
            nonexistent_config = temp_dir / "nonexistent.yaml"
            sys.argv = ["split-real-books.py", "-c", str(nonexistent_config)]

            with pytest.raises(UnboundLocalError):
                split_module.main()
        finally:
            sys.argv = old_argv

    def test_split_creates_multiple_output_directories(
        self, temp_dir, multi_page_pdf, split_module
    ):
        config_path = temp_dir / "multi_config.yaml"
        config_content = f"""- file: {multi_page_pdf}
  offset: 0
  output_directory: {temp_dir / "output1"}
  songs:
      - Song A: 1

- file: {multi_page_pdf}
  offset: 0
  output_directory: {temp_dir / "output2"}
  songs:
      - Song B: 2
"""
        config_path.write_text(config_content)

        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "-c", str(config_path)]
            split_module.main()

            assert (temp_dir / "output1").exists()
            assert (temp_dir / "output2").exists()
            assert (temp_dir / "output1" / "Song A.pdf").exists()
            assert (temp_dir / "output2" / "Song B.pdf").exists()
        finally:
            sys.argv = old_argv


@pytest.mark.characterization
class TestCLICompileMode:
    def test_compile_single_directory(
        self, directory_with_pdfs, temp_dir, split_module
    ):
        import sys

        old_argv = sys.argv

        try:
            sys.argv = [
                "split-real-books.py",
                "--compile-directory",
                str(directory_with_pdfs),
            ]
            split_module.main()

            output_file = Path(f"{directory_with_pdfs}_combined.pdf")
            assert output_file.exists()

            output_file.unlink()
        finally:
            sys.argv = old_argv

    def test_compile_multiple_directories(self, temp_dir, split_module):
        from pypdf import PageObject, PdfWriter

        dir1 = temp_dir / "compile1"
        dir2 = temp_dir / "compile2"
        dir1.mkdir()
        dir2.mkdir()

        for d in [dir1, dir2]:
            writer = PdfWriter()
            writer.add_page(PageObject.create_blank_page(width=612, height=792))
            with open(d / "song.pdf", "wb") as f:
                writer.write(f)

        import sys

        old_argv = sys.argv

        try:
            sys.argv = [
                "split-real-books.py",
                "--compile-directory",
                str(dir1),
                "--compile-directory",
                str(dir2),
            ]
            split_module.main()

            output1 = Path(f"{dir1}_combined.pdf")
            output2 = Path(f"{dir2}_combined.pdf")

            assert output1.exists()
            assert output2.exists()

            output1.unlink()
            output2.unlink()
        finally:
            sys.argv = old_argv

    def test_compile_with_compression(
        self, directory_with_pdfs, temp_dir, split_module
    ):
        import sys

        old_argv = sys.argv

        try:
            sys.argv = [
                "split-real-books.py",
                "--compile-directory",
                str(directory_with_pdfs),
                "--compress",
            ]
            split_module.main()

            output_file = Path(f"{directory_with_pdfs}_combined.pdf")
            assert output_file.exists()

            output_file.unlink()
        finally:
            sys.argv = old_argv

    def test_compile_mode_bypasses_config_reading(
        self, temp_dir, directory_with_pdfs, split_module
    ):
        import sys

        old_argv = sys.argv

        try:
            sys.argv = [
                "split-real-books.py",
                "-c",
                str(temp_dir / "nonexistent.yaml"),
                "--compile-directory",
                str(directory_with_pdfs),
            ]
            split_module.main()

            output_file = Path(f"{directory_with_pdfs}_combined.pdf")
            assert output_file.exists()

            output_file.unlink()
        finally:
            sys.argv = old_argv


@pytest.mark.characterization
class TestCLILogging:
    def test_default_logging_level(self, sample_config_yaml, caplog, split_module):
        import logging
        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "-c", str(sample_config_yaml)]
            args = split_module.parse_args()

            assert args.loglevel == logging.INFO
        finally:
            sys.argv = old_argv

    def test_debug_logging_level(self, split_module):
        import logging
        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "--debug"]
            args = split_module.parse_args()

            assert args.loglevel == logging.DEBUG
        finally:
            sys.argv = old_argv
