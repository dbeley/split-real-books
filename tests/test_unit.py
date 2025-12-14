import pytest


@pytest.mark.unit
class TestReadConfig:
    def test_read_valid_yaml_config(self, sample_config_yaml, split_module):
        config = split_module.read_config(sample_config_yaml)

        assert config is not None
        assert isinstance(config, list)
        assert len(config) == 1
        assert "file" in config[0]
        assert "songs" in config[0]
        assert config[0]["offset"] == 0
        assert config[0]["abbreviation"] == "TEST"

    def test_read_nonexistent_config(self, temp_dir, split_module):
        """Test reading a non-existent config file.

        BUG: Current implementation raises UnboundLocalError instead of
        returning None or a default value. This is existing behavior.
        """
        nonexistent = temp_dir / "nonexistent.yaml"

        with pytest.raises(UnboundLocalError):
            split_module.read_config(nonexistent)

    def test_read_malformed_yaml(self, temp_dir, split_module):
        """Test reading a malformed YAML file.

        BUG: Current implementation raises UnboundLocalError instead of
        returning None or a default value. This is existing behavior.
        """
        malformed_yaml = temp_dir / "malformed.yaml"
        malformed_yaml.write_text("{ invalid: yaml: content: }")

        with pytest.raises(UnboundLocalError):
            split_module.read_config(malformed_yaml)


@pytest.mark.unit
class TestApplyWriterCompression:
    def test_compression_with_empty_writer(self, split_module):
        from pypdf import PdfWriter

        writer = PdfWriter()
        split_module.apply_writer_compression(writer, level=9)

    def test_compression_with_pages(self, sample_pdf, split_module):
        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(sample_pdf)
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        split_module.apply_writer_compression(writer, level=9)


@pytest.mark.unit
class TestParseArgs:
    def test_default_arguments(self, monkeypatch, split_module):
        monkeypatch.setattr("sys.argv", ["split-real-books.py"])
        args = split_module.parse_args()

        assert args.config_file == "config.yaml"
        assert args.compile_directory == []
        assert args.compress is False
        assert args.loglevel == 20  # logging.INFO

    def test_debug_flag(self, monkeypatch, split_module):
        monkeypatch.setattr("sys.argv", ["split-real-books.py", "--debug"])
        args = split_module.parse_args()

        assert args.loglevel == 10  # logging.DEBUG

    def test_custom_config_file(self, monkeypatch, split_module):
        monkeypatch.setattr("sys.argv", ["split-real-books.py", "-c", "custom.yaml"])
        args = split_module.parse_args()

        assert args.config_file == "custom.yaml"

    def test_compile_directory_single(self, monkeypatch, split_module):
        monkeypatch.setattr(
            "sys.argv", ["split-real-books.py", "--compile-directory", "dir1"]
        )
        args = split_module.parse_args()

        assert args.compile_directory == ["dir1"]

    def test_compile_directory_multiple(self, monkeypatch, split_module):
        monkeypatch.setattr(
            "sys.argv",
            [
                "split-real-books.py",
                "--compile-directory",
                "dir1",
                "--compile-directory",
                "dir2",
            ],
        )
        args = split_module.parse_args()

        assert args.compile_directory == ["dir1", "dir2"]

    def test_compress_flag(self, monkeypatch, split_module):
        monkeypatch.setattr(
            "sys.argv",
            ["split-real-books.py", "--compile-directory", "dir1", "--compress"],
        )
        args = split_module.parse_args()

        assert args.compress is True
