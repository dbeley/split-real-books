# split-real-books

Simple script to split pdf files (in my use-case real books) into multiple
files thanks to a configuration file. It can now also compile the generated
PDFs into a single song book with a convenient table of contents.

# Configuration

Check `config.example.yaml` for the configuration format.

# Usage

## Split PDFs based on the configuration

```
python split-real-books.py
```

## Compile the generated PDFs into a single book

Once the songs have been extracted you can merge the PDFs that live in an
output folder (for example `output_songs`) into a single lightweight PDF with
an automatically generated table of contents:

```
python split-real-books.py --compile-directory output_songs --compress
```

The command above creates `CombinedRealBook.pdf` in `output_songs/`. Every song
is listed alphabetically in the PDF outline so you can quickly jump to any
sheet. The optional `--compress` flag applies additional stream compression to
keep the resulting file small enough for mobile use.

If you run the splitter against a configuration that contains several
`output_directory` entries, you can automatically compile each of them right
after the split with:

```
python split-real-books.py --compile-from-config
```

Additional options:

- `--compiled-filename`: customise the name of the merged PDF (defaults to
  `CombinedRealBook.pdf`).
- `--compile-directory`: can be passed multiple times to merge several folders
  in one run.
- `--compress`: reduce the size of the generated compilation by compressing the
  internal PDF streams.
