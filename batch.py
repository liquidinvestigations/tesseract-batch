#!/usr/bin/env python3

import logging
import os
import subprocess
import time


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

INPUT = os.getenv('INPUT', '/input')
OUTPUT = os.getenv('OUTPUT', '/output')
NICE = int(os.getenv('NICE', '9'))
LANGUAGE = os.getenv('LANGUAGE', 'eng')


def get_languages():
    langs = subprocess.check_output("tesseract --list-langs | tail -n +2", shell=True).decode().split()
    log.info('Tesseract has loaded %s languages.', len(langs))
    return set(langs)


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
ALL_LANGUAGES = get_languages()
for code in LANGUAGE.split('+'):
    assert code in ALL_LANGUAGES


def walk_files():
    for root, _, files in os.walk(INPUT):
        for filename in files:
            full_path = os.path.join(root, filename)
            if os.path.splitext(full_path)[-1] in ALL_EXTENSIONS:
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

    output_stem = os.path.join(OUTPUT, md5[0:2], md5[2:4], md5[4:6], md5)
    output_path = output_stem + '.pdf'
    if os.path.exists(output_path):
        return '%s skipped, output already exists' % image_path

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return run_tesseract(image_path, output_path)


def run_tesseract(image_path, output_path):
    t1 = time.time()
    args = [
        'nice', '-n', str(NICE),
        'pdf2pdfocr.py', '-i', image_path, '-o', output_path,
        '-l', LANGUAGE,
        '-x', '--oem 1 --psm 1',
    ]
    try:
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return '%s done (%.2f sec)' % (image_path, time.time() - t1)
    except subprocess.CalledProcessError as e:
        return '%s failed: %s (%.2f sec)' % (image_path, e, time.time() - t1)


def main():
    t0 = time.time()
    count = 0
    log.info('workers started.')

    for r in map(process, walk_files()):
        log.info('[%3.2f] %s', time.time() - t0, r)
        count += 1

    log.info('all done, %s documents in %s seconds', count, int(time.time() - t0))


if __name__ == '__main__':
    main()
