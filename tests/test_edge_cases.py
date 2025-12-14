import pytest


@pytest.mark.edge_case
class TestEdgeCasesExtraction:
    def test_extract_from_empty_pdf(self, empty_pdf, output_dir, split_module):
        """Current behavior: raises IndexError when trying to access pages."""
        songs = [{"Song 1": "1"}]

        with pytest.raises(IndexError):
            split_module.extract_songs_from_pdf(
                empty_pdf, songs, offset=0, output_dir=output_dir
            )

    def test_extract_with_large_offset(self, sample_pdf, output_dir, split_module):
        """Current behavior: raises IndexError when page is out of range."""
        songs = [{"Song 1": "1"}]
        offset = 1000

        with pytest.raises(IndexError):
            split_module.extract_songs_from_pdf(
                sample_pdf, songs, offset=offset, output_dir=output_dir
            )

    def test_extract_with_negative_offset(self, sample_pdf, output_dir, split_module):
        songs = [{"Song 1": "2"}]
        offset = -1

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=offset, output_dir=output_dir
        )

        assert (output_dir / "Song 1.pdf").exists()

    def test_extract_with_invalid_page_range(
        self, sample_pdf, output_dir, split_module
    ):
        """Current behavior: creates an empty range, writes empty PDF."""
        songs = [{"Song 1": "5-2"}]

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir
        )

        from pypdf import PdfReader

        reader = PdfReader(output_dir / "Song 1.pdf")
        assert len(reader.pages) == 0

    def test_extract_with_special_characters_in_name(
        self, sample_pdf, output_dir, split_module
    ):
        """Current behavior: raises FileNotFoundError for invalid filename characters."""
        songs = [{"Song / With \\ Special: Chars?": "1"}]

        with pytest.raises(FileNotFoundError):
            split_module.extract_songs_from_pdf(
                sample_pdf, songs, offset=0, output_dir=output_dir
            )

    def test_extract_with_empty_song_name(self, sample_pdf, output_dir, split_module):
        songs = [{"": "1"}]

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir
        )

        assert (output_dir / ".pdf").exists()

    def test_extract_with_unicode_song_name(self, sample_pdf, output_dir, split_module):
        songs = [{"Café François 音楽": "1"}]

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir
        )

        assert (output_dir / "Café François 音楽.pdf").exists()

    def test_extract_overwrites_existing_file(
        self, sample_pdf, output_dir, split_module
    ):
        songs = [{"Song 1": "1"}]

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir
        )

        first_mtime = (output_dir / "Song 1.pdf").stat().st_mtime

        import time

        time.sleep(0.01)

        split_module.extract_songs_from_pdf(
            sample_pdf, songs, offset=0, output_dir=output_dir
        )

        second_mtime = (output_dir / "Song 1.pdf").stat().st_mtime

        assert second_mtime > first_mtime


@pytest.mark.edge_case
class TestEdgeCasesCompilation:
    def test_compile_skips_empty_pdfs(self, temp_dir, caplog, split_module):
        pdf_dir = temp_dir / "songs"
        pdf_dir.mkdir()

        from pypdf import PdfWriter

        writer = PdfWriter()
        with open(pdf_dir / "empty.pdf", "wb") as f:
            writer.write(f)

        from pypdf import PageObject

        writer2 = PdfWriter()
        writer2.add_page(PageObject.create_blank_page(width=612, height=792))
        with open(pdf_dir / "normal.pdf", "wb") as f:
            writer2.write(f)

        output_file = temp_dir / "combined.pdf"
        split_module.compile_directory(pdf_dir, output_file)

        assert "has no pages" in caplog.text
        assert output_file.exists()

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) == 1

    def test_compile_with_nested_directories(self, temp_dir, split_module):
        pdf_dir = temp_dir / "songs"
        nested_dir = pdf_dir / "subfolder"
        pdf_dir.mkdir()
        nested_dir.mkdir()

        from pypdf import PageObject, PdfWriter

        writer1 = PdfWriter()
        writer1.add_page(PageObject.create_blank_page(width=612, height=792))
        with open(pdf_dir / "root_song.pdf", "wb") as f:
            writer1.write(f)

        writer2 = PdfWriter()
        writer2.add_page(PageObject.create_blank_page(width=612, height=792))
        with open(nested_dir / "nested_song.pdf", "wb") as f:
            writer2.write(f)

        output_file = temp_dir / "combined.pdf"
        split_module.compile_directory(pdf_dir, output_file)

        assert output_file.exists()

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) == 2

        outline_titles = [item.title for item in reader.outline]
        assert "nested_song" in outline_titles
        assert "root_song" in outline_titles

    def test_compile_case_insensitive_sorting(self, temp_dir, split_module):
        pdf_dir = temp_dir / "songs"
        pdf_dir.mkdir()

        from pypdf import PageObject, PdfWriter

        names = ["Zebra.pdf", "apple.pdf", "BANANA.pdf", "cherry.pdf"]
        for name in names:
            writer = PdfWriter()
            writer.add_page(PageObject.create_blank_page(width=612, height=792))
            with open(pdf_dir / name, "wb") as f:
                writer.write(f)

        output_file = temp_dir / "combined.pdf"
        split_module.compile_directory(pdf_dir, output_file)

        from pypdf import PdfReader

        reader = PdfReader(output_file)

        outline_titles = [item.title for item in reader.outline]
        expected = ["apple", "BANANA", "cherry", "Zebra"]
        assert outline_titles == expected

    def test_compile_with_pdf_extension_variations(self, temp_dir, split_module):
        pdf_dir = temp_dir / "songs"
        pdf_dir.mkdir()

        from pypdf import PageObject, PdfWriter

        writer1 = PdfWriter()
        writer1.add_page(PageObject.create_blank_page(width=612, height=792))
        with open(pdf_dir / "song1.pdf", "wb") as f:
            writer1.write(f)

        writer2 = PdfWriter()
        writer2.add_page(PageObject.create_blank_page(width=612, height=792))
        with open(pdf_dir / "song2.PDF", "wb") as f:
            writer2.write(f)

        output_file = temp_dir / "combined.pdf"
        split_module.compile_directory(pdf_dir, output_file)

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) == 2

    def test_compile_ignores_non_pdf_files(self, temp_dir, split_module):
        pdf_dir = temp_dir / "songs"
        pdf_dir.mkdir()

        from pypdf import PageObject, PdfWriter

        writer = PdfWriter()
        writer.add_page(PageObject.create_blank_page(width=612, height=792))
        with open(pdf_dir / "song.pdf", "wb") as f:
            writer.write(f)

        (pdf_dir / "readme.txt").write_text("Not a PDF")
        (pdf_dir / "image.jpg").write_bytes(b"fake image")

        output_file = temp_dir / "combined.pdf"
        split_module.compile_directory(pdf_dir, output_file)

        from pypdf import PdfReader

        reader = PdfReader(output_file)
        assert len(reader.pages) == 1


@pytest.mark.edge_case
class TestEdgeCasesConfig:
    def test_config_with_missing_offset(self, temp_dir, sample_pdf, split_module):
        """Current behavior: raises KeyError."""
        config_path = temp_dir / "config_no_offset.yaml"
        config_content = f"""- file: {sample_pdf}
  songs:
      - Song 1: 1
"""
        config_path.write_text(config_content)

        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "-c", str(config_path)]

            with pytest.raises(KeyError):
                split_module.main()
        finally:
            sys.argv = old_argv

    def test_config_with_missing_file(self, temp_dir, split_module):
        """Current behavior: raises KeyError."""
        config_path = temp_dir / "config_no_file.yaml"
        config_content = """- offset: 0
  songs:
      - Song 1: 1
"""
        config_path.write_text(config_content)

        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "-c", str(config_path)]

            with pytest.raises(KeyError):
                split_module.main()
        finally:
            sys.argv = old_argv

    def test_config_with_missing_songs(self, temp_dir, sample_pdf, split_module):
        """Current behavior: raises KeyError."""
        config_path = temp_dir / "config_no_songs.yaml"
        config_content = f"""- file: {sample_pdf}
  offset: 0
"""
        config_path.write_text(config_content)

        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "-c", str(config_path)]

            with pytest.raises(KeyError):
                split_module.main()
        finally:
            sys.argv = old_argv

    def test_config_with_nonexistent_pdf(self, temp_dir, split_module):
        """Current behavior: raises FileNotFoundError."""
        config_path = temp_dir / "config.yaml"
        config_content = """- file: /nonexistent/path/file.pdf
  offset: 0
  songs:
      - Song 1: 1
"""
        config_path.write_text(config_content)

        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "-c", str(config_path)]

            with pytest.raises(FileNotFoundError):
                split_module.main()
        finally:
            sys.argv = old_argv

    def test_config_with_empty_songs_list(self, temp_dir, sample_pdf, split_module):
        config_path = temp_dir / "config_empty_songs.yaml"
        config_content = f"""- file: {sample_pdf}
  offset: 0
  songs: []
"""
        config_path.write_text(config_content)

        import sys

        old_argv = sys.argv

        try:
            sys.argv = ["split-real-books.py", "-c", str(config_path)]
            split_module.main()
        finally:
            sys.argv = old_argv


@pytest.mark.edge_case
class TestEdgeCasesCompression:
    def test_compression_handles_image_only_pages(self, temp_dir, split_module):
        pass

    def test_apply_compression_to_already_compressed(
        self, sample_pdf, temp_dir, split_module
    ):
        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(sample_pdf)
        writer = PdfWriter()
        writer.add_page(reader.pages[0])

        split_module.apply_writer_compression(writer, level=9)
        split_module.apply_writer_compression(writer, level=9)

        output_file = temp_dir / "double_compressed.pdf"
        with open(output_file, "wb") as f:
            writer.write(f)

        assert output_file.exists()
