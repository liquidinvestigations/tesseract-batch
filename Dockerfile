FROM liquidinvestigations/pdf2pdfocr

# fall back to root, our collections are owned by root
USER 0
ENV OMP_THREAD_LIMIT 1

ADD batch.py .
ADD examples /examples
ENTRYPOINT ./batch.py
