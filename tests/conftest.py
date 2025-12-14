import importlib.util
from pathlib import Path

import pytest
from pypdf import PdfWriter


def _get_split_module():
    """Import the split-real-books module dynamically.

    This helper function uses dynamic path resolution to find the main module
    relative to the test directory, making tests portable across environments.
    """
    test_dir = Path(__file__).parent
    module_path = test_dir.parent / "split-real-books.py"

    spec = importlib.util.spec_from_file_location("split_real_books", module_path)
    split_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(split_module)
    return split_module


@pytest.fixture(scope="session")
def split_module():
    return _get_split_module()


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def sample_pdf(temp_dir):
    pdf_path = temp_dir / "sample.pdf"
    writer = PdfWriter()
    from pypdf import PageObject

    for i in range(5):
        page = PageObject.create_blank_page(width=612, height=792)  # Letter size
        writer.add_page(page)

    with open(pdf_path, "wb") as f:
        writer.write(f)

    return pdf_path


@pytest.fixture
def multi_page_pdf(temp_dir):
    pdf_path = temp_dir / "multi_page.pdf"
    writer = PdfWriter()
    from pypdf import PageObject

    for i in range(10):
        page = PageObject.create_blank_page(width=612, height=792)
        writer.add_page(page)

    with open(pdf_path, "wb") as f:
        writer.write(f)

    return pdf_path


@pytest.fixture
def sample_config_dict():
    return [
        {
            "file": "/path/to/file.pdf",
            "offset": 0,
            "abbreviation": "TEST",
            "output_directory": "test_output",
            "songs": [
                {"Song 1": "1"},
                {"Song 2": "2-3"},
                {"Song 3": "4"},
            ],
        }
    ]


@pytest.fixture
def sample_config_yaml(temp_dir, sample_pdf):
    config_path = temp_dir / "config.yaml"
    config_content = f"""- file: {sample_pdf}
  offset: 0
  abbreviation: TEST
  output_directory: {temp_dir / "output"}
  songs:
      - Song 1: 1
      - Song 2: 2-3
      - Song 3: 4
"""
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def empty_pdf(temp_dir):
    pdf_path = temp_dir / "empty.pdf"
    writer = PdfWriter()
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return pdf_path


@pytest.fixture
def output_dir(temp_dir):
    out_dir = temp_dir / "output"
    out_dir.mkdir(exist_ok=True)
    return out_dir


@pytest.fixture
def directory_with_pdfs(temp_dir):
    pdf_dir = temp_dir / "songs"
    pdf_dir.mkdir(exist_ok=True)
    from pypdf import PageObject

    song_names = ["A Song.pdf", "B Song.pdf", "C Song.pdf", "z Last Song.pdf"]

    for song_name in song_names:
        writer = PdfWriter()
        for _ in range(1 + (len(song_name) % 2)):
            page = PageObject.create_blank_page(width=612, height=792)
            writer.add_page(page)

        with open(pdf_dir / song_name, "wb") as f:
            writer.write(f)

    return pdf_dir
