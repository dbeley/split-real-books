from pathlib import Path

import pytest


@pytest.mark.integration
class TestExtractSongsFromPdf:
    def test_extract_single_page_song(self, sample_pdf, output_dir, split_module):
        songs = [{"Song 1": "1"}]

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir
        )

        output_file = output_dir / "Song 1.pdf"
        assert output_file.exists()

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) == 1

    def test_extract_page_range_song(self, sample_pdf, output_dir, split_module):
        songs = [{"Song 2": "2-3"}]

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir
        )

        output_file = output_dir / "Song 2.pdf"
        assert output_file.exists()

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) == 2

    def test_extract_with_offset(self, multi_page_pdf, output_dir, split_module):
        songs = [{"Song 1": "1"}, {"Song 2": "2-3"}]
        offset = 2

        split_module.extract_songs_from_pdf(
            multi_page_pdf, songs, offset=offset, output_dir=output_dir
        )

        assert (output_dir / "Song 1.pdf").exists()
        assert (output_dir / "Song 2.pdf").exists()

    def test_extract_with_abbreviation(self, sample_pdf, output_dir, split_module):
        songs = [{"Song 1": "1"}]

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir, abbreviation="RB"
        )

        output_file = output_dir / "Song 1 (RB).pdf"
        assert output_file.exists()

    def test_extract_multiple_songs(self, sample_pdf, output_dir, split_module):
        songs = [{"Song 1": "1"}, {"Song 2": "2-3"}, {"Song 3": "4-5"}]

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir
        )

        assert (output_dir / "Song 1.pdf").exists()
        assert (output_dir / "Song 2.pdf").exists()
        assert (output_dir / "Song 3.pdf").exists()

    def test_extract_creates_output_directory(self, sample_pdf, temp_dir, split_module):
        nonexistent_dir = temp_dir / "new_output"
        assert not nonexistent_dir.exists()

        songs = [{"Song 1": "1"}]
        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=nonexistent_dir
        )

        assert nonexistent_dir.exists()
        assert (nonexistent_dir / "Song 1.pdf").exists()


@pytest.mark.integration
class TestCompileDirectory:
    def test_compile_empty_directory(self, temp_dir, caplog, split_module):
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        output_file = temp_dir / "output.pdf"

        split_module.compile_directory(empty_dir, output_file)

        assert "No PDF files were found" in caplog.text
        assert not output_file.exists()

    def test_compile_directory_with_pdfs(
        self, directory_with_pdfs, temp_dir, split_module
    ):
        output_file = temp_dir / "combined.pdf"

        split_module.compile_directory(directory_with_pdfs, output_file)

        assert output_file.exists()

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) > 0
        assert len(reader.outline) > 0

    def test_compile_sorts_alphabetically(
        self, directory_with_pdfs, temp_dir, split_module
    ):
        output_file = temp_dir / "combined.pdf"

        split_module.compile_directory(directory_with_pdfs, output_file)

        from pypdf import PdfReader

        reader = PdfReader(output_file)

        outline_titles = [item.title for item in reader.outline]
        assert outline_titles == ["A Song", "B Song", "C Song", "z Last Song"]

    def test_compile_with_compression(
        self, directory_with_pdfs, temp_dir, split_module
    ):
        output_file = temp_dir / "combined_compressed.pdf"

        split_module.compile_directory(directory_with_pdfs, output_file, compress=True)

        assert output_file.exists()

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) > 0

    def test_compile_excludes_output_file(self, temp_dir, split_module):
        pdf_dir = temp_dir / "songs"
        pdf_dir.mkdir()

        from pypdf import PageObject, PdfWriter

        writer = PdfWriter()
        writer.add_page(PageObject.create_blank_page(width=612, height=792))
        with open(pdf_dir / "song1.pdf", "wb") as f:
            writer.write(f)

        output_file = pdf_dir / "combined.pdf"

        split_module.compile_directory(pdf_dir, output_file)

        assert output_file.exists()

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) == 1


@pytest.mark.integration
class TestCompileDirectories:
    def test_compile_single_directory(self, directory_with_pdfs, caplog, split_module):
        split_module.compile_directories([str(directory_with_pdfs)])

        output_file = Path(f"{directory_with_pdfs}_combined.pdf")
        assert output_file.exists()

        output_file.unlink()

    def test_compile_multiple_directories(self, temp_dir, caplog, split_module):
        from pypdf import PageObject, PdfWriter

        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        for d in [dir1, dir2]:
            writer = PdfWriter()
            writer.add_page(PageObject.create_blank_page(width=612, height=792))
            with open(d / "song.pdf", "wb") as f:
                writer.write(f)

        split_module.compile_directories([str(dir1), str(dir2)])

        output1 = Path(f"{dir1}_combined.pdf")
        output2 = Path(f"{dir2}_combined.pdf")

        assert output1.exists()
        assert output2.exists()

        output1.unlink()
        output2.unlink()

    def test_compile_nonexistent_directory(self, temp_dir, caplog, split_module):
        nonexistent = temp_dir / "nonexistent"

        split_module.compile_directories([str(nonexistent)])

        assert "not a directory" in caplog.text

    def test_compile_with_error_continues(self, temp_dir, caplog, split_module):
        from pypdf import PageObject, PdfWriter

        valid_dir = temp_dir / "valid"
        valid_dir.mkdir()
        writer = PdfWriter()
        writer.add_page(PageObject.create_blank_page(width=612, height=792))
        with open(valid_dir / "song.pdf", "wb") as f:
            writer.write(f)

        invalid_dir = temp_dir / "invalid"

        split_module.compile_directories([str(invalid_dir), str(valid_dir)])

        output = Path(f"{valid_dir}_combined.pdf")
        assert output.exists()

        output.unlink()
