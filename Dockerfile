FROM tesseractshadow/tesseract4re

ENV DEBIAN_NONINTERACTIVE=true
RUN apt-get -yqq update && apt-get -yqq install ghostscript

ADD batch.py .
ENTRYPOINT ./batch.py
