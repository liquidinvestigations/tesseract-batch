# tesseract-batch


This docker image consists of a Python script that runs tesseract on all images
and pdfs found in the `DATA` environment variable, outputting the results in
the `OCR` directory.


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
