# tesseract-batch


This docker image consists of a Python script that runs tesseract on all images
and PDFs found at `/input` into PDF files with OCRed text mounted on `/output`.
One PDF file is created for each input file. The file is named after the input
file's md5 hash. The script should keep the CPU saturated until the process is
done.


Here's a script to run it inside a docker container:

        ./run INPUT_DIR OUTPUT_DIR LANGUAGE [WORKER_COUNT] [IMAGE]


Configuration to the script (and therefore the container) is done through envs:

- `OUTPUT_DIR` - data directory to walk for images/pdfs
- `INPUT_DIR` - input directory, default "/input"
- `LANGUAGE` - languages to run the OCR on, separated by the plus sign (`+`), default "eng"
- `WORKER_COUNT` - number of CPU cores to use, default max
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
