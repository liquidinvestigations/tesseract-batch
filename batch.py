#!/usr/bin/env python3

import logging
import multiprocessing
import os
import subprocess
import time


log = multiprocessing.log_to_stderr()
log.setLevel(logging.INFO)


def get_languages():
    langs = subprocess.check_output("tesseract --list-langs | tail -n +2", shell=True).decode().split()
    log.info('Tesseract has loaded %s languages.', len(langs))
    return set(langs)


INPUT = os.getenv('INPUT', '/input')
OUTPUT = os.getenv('OUTPUT', '/output')
NICE = int(os.getenv('NICE', '9'))
LANGUAGE = os.getenv('LANGUAGE', 'eng')
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
assert os.path.isdir(INPUT)
assert os.path.isdir(OUTPUT)


def walk_files():
    log.info('walking through files...')
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
        return 'SKIP %s, output already exists' % image_path

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return run_tesseract(image_path, output_path)


def run_tesseract(image_path, output_path):
    tmp_output_path = output_path + '_tmp'
    t1 = time.time()
    args = [
        'nice', '-n', str(NICE),
        'pdf2pdfocr.py', '-i', image_path, '-o', tmp_output_path,
        '-l', LANGUAGE,
        '-x', '--oem 1 --psm 1',
        '-j', '0.2',
    ]
    try:
        subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.rename(tmp_output_path, output_path)
        return 'DONE (%.2f sec): %s ' % (time.time() - t1, image_path)
    except subprocess.CalledProcessError as e:
        return 'FAIL (%.2f sec): %s: %s' % (time.time() - t1, e, image_path)


def main():
    t0 = time.time()
    count = 0
    log.info('workers started.')
    with multiprocessing.Pool(5) as p:
        for r in p.imap_unordered(process, walk_files(), 1):
            log.info('[%3.2f] %s', time.time() - t0, r)
            count += 1

    log.info('all done, %s documents in %s seconds', count, int(time.time() - t0))


if __name__ == '__main__':
    main()
