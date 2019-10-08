#!/usr/bin/env python3

import logging
import multiprocessing
import os
import subprocess
import tempfile
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
WORKER_CHUNKSIZE = int(os.getenv('WORKER_CHUNKSIZE', '10'))


def walk_files():
    for root, _, files in os.walk(os.path.abspath(DATA_DIR)):
        for filename in files:
            full_path = os.path.join(root, filename)
            if os.path.splitext(full_path)[1] in ALL_EXTENSIONS:
                yield full_path


def pdf_to_tiff(pdf_path, tiff_path):
    args = ['gs', '-dNOPAUSE', '-q', '-r300x300', '-sDEVICE=tiffg4', '-dBATCH', '-sOutputFile=' + tiff_path, pdf_path]
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        log.exception(e)
        return None


def process(image_path):
    md5 = subprocess.check_output(['md5sum', image_path]).decode('latin1').split(' ')[0]

    output_stem = os.path.join(OCR_DIR, md5[0:2], md5[2:4], md5[4:6], md5)
    output_path = output_stem + '.pdf'
    if os.path.exists(output_path):
        return '%s already exists, skipping' % output_path

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.splitext(image_path)[1] == '.pdf':
        with tempfile.NamedTemporaryFile(suffix='.tiff') as f:
            if not pdf_to_tiff(image_path, f.name):
                return '%s could not be converted to tiff'
            return run_tesseract(f.name, output_stem)
    else:
        return run_tesseract(image_path, output_stem)


def run_tesseract(image_path, output_stem):
    t1 = time.time()
    args = ['tesseract', image_path, output_stem, 'txt', 'pdf']
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
        return '%s done (%s sec)' % (image_path, time.time() - t1)
    except subprocess.CalledProcessError as e:
        return '%s failed: %s (%s sec)' % (image_path, e, time.time() - t1)


def main():
    t0 = time.time()
    count = 0
    log.info('started')

    with multiprocessing.Pool(WORKER_COUNT) as p:
        for r in p.imap_unordered(process, list(walk_files()), WORKER_CHUNKSIZE):
            log.info('[%3.2f] %s', time.time() - t0, r)
            count += 1

    log.info('done, %s documents', count)


if __name__ == '__main__':
    main()
