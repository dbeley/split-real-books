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
            if isinstance(pages, int):
                pages = [pages + offset]
            elif isinstance(pages, str):
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
    config = read_config(args.config_file)

    for real_book_config in config:
        output_directory = (
            real_book_config["output_directory"]
            if "output_directory" in real_book_config
            else "output_songs"
        )
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
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel, format=format)
    return args


if __name__ == "__main__":
    main()
