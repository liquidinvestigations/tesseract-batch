#!/usr/bin/env python3

import logging
import multiprocessing
import os
import subprocess
import time


log = multiprocessing.log_to_stderr()
log.setLevel(logging.INFO)


ALL_EXTENSIONS = [
    '.bmp',
    '.jfif',
    '.jpeg',
    '.jpg',
    '.pdf',
    '.png',
    '.tiff',
    '.tif',
    '.gif',
]
DATA_DIR = os.getenv('DATA', '/data')
OCR_DIR = os.getenv('OCR', '/ocr')
WORKER_COUNT = int(os.getenv('WORKER_COUNT', '3'))
WORKER_CHUNKSIZE = int(os.getenv('WORKER_CHUNKSIZE', '1'))
WORKER_NICE = os.getenv('WORKER_NICE', '7')


def get_languages():
    langs = subprocess.check_output(['tesseract', '--list-langs']).decode().split()
    log.info('Tesseract has loaded %s languages.', len(langs))
    return set(langs)


ALL_LANGUAGES = get_languages()


def walk_files():
    for language in os.listdir(DATA_DIR):
        language_path = os.path.abspath(os.path.join(DATA_DIR, language))
        if not os.path.isdir(language_path):
            log.warning("%s is not a directory", language_path)
            continue
        if language not in ALL_LANGUAGES:
            log.warning("%s is not a valid language", language)
            with open(os.path.join(language_path, 'OCR ERROR - INVALID LANGUAGE CODE'), 'w') as f:
                f.write("liquidinvestigations/tesseract-batch: Language code %s is invalid!" % language)

        for root, _, files in os.walk(language_path):
            for filename in files:
                full_path = os.path.join(root, filename)
                if os.path.splitext(full_path)[1] in ALL_EXTENSIONS:
                    yield language, full_path


def pdf_to_tiff(pdf_path, tiff_path):
    args = ['gs', '-dNOPAUSE', '-q', '-r300x300', '-sDEVICE=tiffg4', '-dBATCH', '-sOutputFile=' + tiff_path, pdf_path]
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        log.exception(e)
        return None


def process(args):
    language, image_path = args

    md5 = subprocess.check_output(['md5sum', image_path]).decode('latin1').split(' ')[0]

    output_stem = os.path.join(OCR_DIR, md5[0:2], md5[2:4], md5[4:6], md5)
    output_path = output_stem + '.pdf'
    if os.path.exists(output_path):
        return '%s skipped, output already exists' % image_path

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return run_tesseract(image_path, output_path, language)


def run_tesseract(image_path, output_path, language):
    t1 = time.time()
    args = [
        'nice', '-n', WORKER_NICE,
        'pdf2pdfocr.py', '-i', image_path, '-o', output_path,
        '-l', language,
    ]
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
        return '%s done (%.2f sec)' % (image_path, time.time() - t1)
    except subprocess.CalledProcessError as e:
        return '%s failed: %s (%.2f sec)' % (image_path, e, time.time() - t1)


def main():
    log.info('copying example files...')
    subprocess.check_call(['cp', '-a', '/examples/.', DATA_DIR])

    t0 = time.time()
    count = 0
    log.info('copying done.')
    log.info('workers started.')

    with multiprocessing.Pool(WORKER_COUNT) as p:
        for r in p.imap_unordered(process, walk_files(), WORKER_CHUNKSIZE):
            log.info('[%3.2f] %s', time.time() - t0, r)
            count += 1

    log.info('all done, %s documents in %s seconds', count, int(time.time() - t0))


if __name__ == '__main__':
    main()
