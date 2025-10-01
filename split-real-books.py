# Split real books into individual files
from __future__ import annotations

import argparse
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from pypdf import PdfReader, PdfWriter
from yaml import YAMLError, safe_load

DEFAULT_COMPILED_NAME = "CombinedRealBook.pdf"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SongDefinition:
    """Description of a song to extract from a real book."""

    name: str
    pages: tuple[int, ...]


def read_config(config_file: str) -> List[dict]:
    """Load the YAML configuration file."""

    config_path = Path(config_file)
    try:
        with config_path.open("r", encoding="utf-8") as file_obj:
            config = safe_load(file_obj) or []
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Config file '{config_path}' was not found."
        ) from exc
    except YAMLError as exc:  # pragma: no cover - malformed YAML
        raise ValueError(
            f"Config file '{config_path}' contains invalid YAML: {exc}"
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive logging
        raise RuntimeError(
            f"Failed to load configuration from '{config_path}': {exc}"
        ) from exc

    if not isinstance(config, list):
        raise ValueError(
            "The configuration root must be a list of real book definitions."
        )

    return config


def _parse_pages(page_spec: object, offset: int) -> Sequence[int]:
    """Return the list of 1-based pages derived from *page_spec*."""

    if isinstance(page_spec, int):
        return [page_spec + offset]

    if isinstance(page_spec, str):
        spec = page_spec.strip()
        if "-" in spec:
            start_str, end_str = spec.split("-", maxsplit=1)
            start, end = int(start_str), int(end_str)
            if end < start:
                raise ValueError("The end of the range cannot be smaller than the start.")
            return [page + offset for page in range(start, end + 1)]
        return [int(spec) + offset]

    if isinstance(page_spec, Sequence) and not isinstance(page_spec, (bytes, str)):
        pages: list[int] = []
        for spec in page_spec:
            pages.extend(_parse_pages(spec, offset))
        return pages

    raise TypeError(
        "Page specifications must be integers, strings in the form 'start-end', or sequences "
        "of those values."
    )


def _parse_song_definition(song_data: object, *, offset: int) -> SongDefinition:
    if not isinstance(song_data, dict):
        raise TypeError("Song definitions must be mappings of names to page specifications.")
    if len(song_data) != 1:
        raise ValueError("Song definitions must contain exactly one song name.")

    (name, page_spec), = song_data.items()

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Song names must be non-empty strings.")

    pages = tuple(int(page) for page in _parse_pages(page_spec, offset))
    if not pages:
        raise ValueError(f"Song '{name}' does not reference any pages.")

    return SongDefinition(name=name.strip(), pages=pages)


def extract_songs_from_pdf(
    input_pdf: Path | str,
    songs: Sequence[SongDefinition],
    output_dir: Path | str,
    abbreviation: str = "",
) -> None:
    source_path = Path(input_pdf)
    if not source_path.is_file():
        raise FileNotFoundError(source_path)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with source_path.open("rb") as pdf_file:
        reader = PdfReader(pdf_file)
        total_pages = len(reader.pages)

        for song in songs:
            invalid_page = next(
                (page for page in song.pages if page < 1 or page > total_pages),
                None,
            )
            if invalid_page is not None:
                logger.error(
                    "Page %s for '%s' is outside the bounds of '%s' (1-%s).",
                    invalid_page,
                    song.name,
                    input_pdf,
                    total_pages,
                )
                continue

            writer = PdfWriter()
            for page_number in song.pages:
                writer.add_page(reader.pages[page_number - 1])

            filename = f"{song.name}.pdf"
            if abbreviation:
                filename = f"{song.name} ({abbreviation}).pdf"

            output_file = output_path / filename
            with output_file.open("wb") as file_obj:
                writer.write(file_obj)

            logger.info("Created: %s", output_file)


def main():
    args = parse_args()

    if args.compile_directory:
        compile_directories(
            args.compile_directory,
            compiled_filename=args.compiled_filename,
            compress=args.compress,
        )
        return

    start_time = time.time()

    try:
        config = read_config(args.config_file)
    except Exception as exc:  # pragma: no cover - fatal configuration issue
        logger.error(exc)
        raise SystemExit(1) from exc

    output_directories: set[Path] = set()

    for index, real_book_config in enumerate(config, start=1):
        if not isinstance(real_book_config, dict):
            logger.error(
                "Configuration entry #%s must be a mapping. Skipping: %s",
                index,
                real_book_config,
            )
            continue

        try:
            pdf_path_raw = real_book_config["file"]
            songs_data = real_book_config["songs"]
        except KeyError as exc:
            logger.error(
                "Missing required key '%s' in configuration entry #%s: %s",
                exc.args[0],
                index,
                real_book_config,
            )
            continue

        try:
            pdf_path = Path(pdf_path_raw)
        except TypeError:
            logger.error(
                "Invalid path for 'file' in configuration entry #%s: %s",
                index,
                pdf_path_raw,
            )
            continue

        if not isinstance(songs_data, list):
            logger.error(
                "Expected 'songs' to be a list in configuration entry #%s: %s",
                index,
                real_book_config,
            )
            continue

        try:
            offset = int(real_book_config.get("offset", 0))
        except (TypeError, ValueError):
            logger.error(
                "Offset must be an integer for configuration entry #%s: %s",
                index,
                real_book_config,
            )
            continue

        output_directory_raw = real_book_config.get("output_directory", "output_songs")
        try:
            output_directory = Path(output_directory_raw)
        except TypeError:
            logger.error(
                "Invalid output directory in configuration entry #%s: %s",
                index,
                output_directory_raw,
            )
            continue

        abbreviation = str(real_book_config.get("abbreviation", "") or "").strip()

        song_definitions: list[SongDefinition] = []
        for song_index, song_data in enumerate(songs_data, start=1):
            try:
                song = _parse_song_definition(song_data, offset=offset)
            except (TypeError, ValueError) as exc:
                logger.error(
                    "Invalid song definition at entry #%s song #%s: %s",
                    index,
                    song_index,
                    exc,
                )
                continue
            song_definitions.append(song)

        if not song_definitions:
            logger.warning(
                "No valid songs were defined for configuration entry #%s (%s).",
                index,
                pdf_path,
            )
            continue

        try:
            extract_songs_from_pdf(
                pdf_path,
                song_definitions,
                output_directory,
                abbreviation,
            )
        except FileNotFoundError:
            logger.error("Input PDF '%s' was not found.", pdf_path)
            continue

        output_directories.add(output_directory)

    if args.compile_from_config and output_directories:
        compile_directories(
            [str(path) for path in sorted(output_directories)],
            compiled_filename=args.compiled_filename,
            compress=args.compress,
        )

    logger.info("Runtime : %.2f seconds.", time.time() - start_time)


def parse_args() -> argparse.Namespace:
    log_format = "%(levelname)s :: %(message)s"
    parser = argparse.ArgumentParser(
        description="Split real books into individual files."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-c",
        "--config_file",
        help='Path to the config file (default: "config.yaml")',
        type=str,
        default="config.yaml",
    )
    parser.add_argument(
        "--compile-directory",
        help="Compile the PDFs contained in the provided directory into a single file."
        " Can be specified multiple times to compile several folders at once.",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--compile-from-config",
        help="Compile every output directory that was defined in the configuration.",
        action="store_true",
    )
    parser.add_argument(
        "--compiled-filename",
        help=(
            "Name of the compiled PDF file."
            f" Defaults to '{DEFAULT_COMPILED_NAME}'."
        ),
        default=DEFAULT_COMPILED_NAME,
    )
    parser.add_argument(
        "--compress",
        help="Compress PDF content streams when compiling to reduce the final file size.",
        action="store_true",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel, format=log_format)
    return args


def compile_directories(
    directories: Iterable[str],
    *,
    compiled_filename: str,
    compress: bool = False,
) -> None:
    for directory in directories:
        directory_path = Path(directory).resolve()
        if not directory_path.is_dir():
            logger.warning("Skipping '%s' because it is not a directory.", directory_path)
            continue
        output_file = directory_path / compiled_filename
        try:
            compile_directory(directory_path, output_file, compress=compress)
        except Exception as exc:  # pragma: no cover - unexpected failure
            logger.error("Failed to compile '%s': %s", directory_path, exc)


def compile_directory(
    directory: Path | str,
    output_file: Path | str,
    compress: bool = False,
) -> None:
    directory_path = Path(directory).resolve()
    output_path = Path(output_file).resolve()

    pdf_files = []
    for candidate in directory_path.rglob("*.pdf"):
        candidate_resolved = candidate.resolve()
        if candidate_resolved == output_path:
            continue
        pdf_files.append(candidate_resolved)

    pdf_files.sort(key=lambda path: path.stem.casefold())

    if not pdf_files:
        logger.warning("No PDF files were found in '%s'.", directory_path)
        return

    writer = PdfWriter()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    for pdf_path in pdf_files:
        song_name = pdf_path.stem
        with pdf_path.open("rb") as file_obj:
            reader = PdfReader(file_obj)
            page_count = len(reader.pages)

            if page_count == 0:
                logger.warning("Skipping '%s' because it has no pages.", pdf_path)
                continue

            first_page_index = len(writer.pages)

            for page in reader.pages:
                if compress:
                    page.compress_content_streams()
                writer.add_page(page)

            destination_page = writer.pages[first_page_index]
            writer.add_outline_item(song_name, destination_page)

    with output_path.open("wb") as out_file:
        writer.write(out_file)

    logger.info("Created compilation: %s", output_path)


if __name__ == "__main__":
    main()
