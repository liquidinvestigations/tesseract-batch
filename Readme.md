# tesseract-batch


This docker image consists of a Python script that runs tesseract on all images
and pdfs found at `$DATA_DIR/<language-code>`, outputting the results in the
`$OCR_DIR` directory.


Here's how to run it:

        docker run \
                --user "$(id -u):$(id -g)" \
                -v $(pwd)/test-files:/data \
                -v $(pwd)/output:/ocr \
                liquidinvestigations/tesseract-batch


Configuration is done through envs:

- `DATA_DIR` - data directory to walk for images/pdfs
- `OCR_DIR` - output directory
- `WORKER_COUNT` - process pool size
- `WORKER_CHUNKSIZE` - chunk size for `multiprocessing.Pool.imap_unordered`


## Supported languages

See the [Tesseract 4.0 documentation](https://github.com/tesseract-ocr/tesseract/wiki/Data-Files#data-files-for-version-400-november-29-2016) for the language codes. Available options include:

- `eng` - English
- `deu` - German
- `fra` - French
- `ron` - Romanian
- `fin` - Finnish
- `nld` - Dutch, Flemish
- `nor` - Norwegian

You can also chain two or more languages. Name the directory `eng+deu+fra` to use 3 language models.
