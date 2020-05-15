# tesseract-batch


This docker image consists of a Python script that runs tesseract on all images
and PDFs found at `/input` into PDF files with OCRed text mounted on `/output`.
One PDF file is created for each input file. The file is named after the input
file's md5 hash. The script should keep the CPU saturated until the process is
done.


Here's how to run it:

        ./run INPUT_DIR OUTPUT_DIR LANGUAGE


Configuration to the is done through envs:

- `OUTPUT_DIR` - data directory to walk for images/pdfs
- `INPUT_DIR` - output directory
- `LANGUAGE` - languages to run the OCR on, separated by the plus sign (`+`)
- `NICE` - parameter sent to the `nice` system utility for the OCR process, default 9


## Supported languages

See the [Tesseract 4.0 documentation](https://github.com/tesseract-ocr/tesseract/wiki/Data-Files#data-files-for-version-400-november-29-2016) for the language codes. Available options include:

- `eng` - English
- `deu` - German
- `fra` - French
- `ron` - Romanian
- `fin` - Finnish
- `nld` - Dutch, Flemish
- `nor` - Norwegian

You can also chain two or more languages. Use `eng+deu+fra` to use the best result for each document.
