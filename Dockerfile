FROM liquidinvestigations/pdf2pdfocr

ENV OMP_THREAD_LIMIT 1
# fall back to root, our collections are owned by root
USER 0

ADD batch.py .
ADD examples /examples
ENTRYPOINT ./batch.py
