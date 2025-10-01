# Split real books into individual files
import argparse
import logging
import os
import time

from pypdf import PdfReader, PdfWriter
from yaml import Loader, load

logger = logging.getLogger()
start_time = time.time()


def read_config(config_file):
    try:
        with open(config_file, "r") as f:
            config = load(f, Loader=Loader)
    except Exception as e:
        logger.error(e)
    return config


def extract_songs_from_pdf(input_pdf, config, offset, output_dir, abbreviation=""):
    """
    Extracts specific pages from a PDF and creates separate PDFs for each song.

    Args:
        input_pdf (str): Path to the input PDF file.
        config (list): Configuration object as a list of dictionaries.
                       Example: [{"Song name 1": 14}, {"Song name 2": "15-16"}]
        offset (int): Offset to apply to the pages.
        output_dir (str): Directory to save the extracted PDFs.
        abbreviation (optional, str): Will be used in the output filename.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the PDF file
    reader = PdfReader(input_pdf)

    for song in config:
        for song_name, pages in song.items():
            # Handle single page or page range
            try:
                pages = int(pages)
                pages = [pages + offset]
            except ValueError:
                start, end = map(int, pages.split("-"))
                pages = list(range(start + offset, end + offset + 1))

            # Create a new PDF for the song
            writer = PdfWriter()
            for page_number in pages:
                # Adjust page index (PyPDF2 is zero-based)
                writer.add_page(reader.pages[page_number - 1])

            # Save the extracted pages to a new file
            if abbreviation:
                output_file = os.path.join(
                    output_dir, f"{song_name} ({abbreviation}).pdf"
                )
            else:
                output_file = os.path.join(output_dir, f"{song_name}.pdf")
            with open(output_file, "wb") as f:
                writer.write(f)

            logger.info(f"Created: {output_file}")


def main():
    args = parse_args()

    if args.compile_directory:
        compile_directories(
            args.compile_directory,
            args.compiled_filename,
            compress=args.compress,
        )
        return

    config = read_config(args.config_file)

    output_directories = set()

    for real_book_config in config:
        output_directory = (
            real_book_config["output_directory"]
            if "output_directory" in real_book_config
            else "output_songs"
        )
        output_directories.add(output_directory)
        abbreviation = (
            real_book_config["abbreviation"]
            if "abbreviation" in real_book_config
            else ""
        )
        extract_songs_from_pdf(
            real_book_config["file"],
            real_book_config["songs"],
            real_book_config["offset"],
            output_directory,
            abbreviation,
        )

    if args.compile_from_config:
        compile_directories(
            sorted(output_directories),
            args.compiled_filename,
            compress=args.compress,
        )

    logger.info("Runtime : %.2f seconds." % (time.time() - start_time))


def parse_args():
    format = "%(levelname)s :: %(message)s"
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
        "--compiled-filename",
        help="Filename of the generated compilation PDF (default: CombinedRealBook.pdf).",
        default="CombinedRealBook.pdf",
    )
    parser.add_argument(
        "--compile-from-config",
        help="After splitting, compile each output directory defined in the config.",
        action="store_true",
    )
    parser.add_argument(
        "--compress",
        help="Compress PDF content streams when compiling to reduce the final file size.",
        action="store_true",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel, format=format)
    return args


def compile_directories(directories, compiled_filename, compress=False):
    """Compile a list of directories into combined PDF files.

    Args:
        directories (list[str]): List of directories containing PDFs to merge.
        compiled_filename (str): Name of the combined PDF that will be created in
            each directory.
        compress (bool, optional): Compress PDF content streams before merging.
    """

    for directory in directories:
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            logger.warning(f"Skipping '{directory}' because it is not a directory.")
            continue
        output_file = os.path.join(directory, compiled_filename)
        try:
            compile_directory(directory, output_file, compress=compress)
        except Exception as exc:
            logger.error(f"Failed to compile '{directory}': {exc}")


def compile_directory(directory, output_file, compress=False):
    """Compile all PDF files in a directory into a single PDF.

    The generated PDF features a table of contents that lists every song in
    alphabetical order. The outline entries directly link to the first page of
    each song.

    Args:
        directory (str): Directory that contains the PDFs to be merged.
        output_file (str): Path of the resulting combined PDF.
        compress (bool, optional): Compress PDF content streams before merging to
            reduce the file size. Defaults to False.
    """

    output_file = os.path.abspath(output_file)

    pdf_files = [
        os.path.abspath(os.path.join(root, filename))
        for root, _, filenames in os.walk(directory)
        for filename in filenames
        if filename.lower().endswith(".pdf")
        and os.path.abspath(os.path.join(root, filename)) != output_file
    ]

    if not pdf_files:
        logger.warning(f"No PDF files were found in '{directory}'.")
        return

    pdf_files.sort(key=lambda path: os.path.splitext(os.path.basename(path))[0].casefold())

    writer = PdfWriter()

    for pdf_path in pdf_files:
        song_name = os.path.splitext(os.path.basename(pdf_path))[0]
        with open(pdf_path, "rb") as file_obj:
            reader = PdfReader(file_obj)
            page_count = len(reader.pages)

            if page_count == 0:
                logger.warning(f"Skipping '{pdf_path}' because it has no pages.")
                continue

            first_page_index = len(writer.pages)

            for page in reader.pages:
                if compress:
                    page.compress_content_streams()
                writer.add_page(page)

            writer.add_outline_item(song_name, first_page_index)

    with open(output_file, "wb") as out_file:
        writer.write(out_file)

    logger.info(f"Created compilation: {output_file}")


if __name__ == "__main__":
    main()
