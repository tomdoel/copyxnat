FROM python:3.9-slim

COPY /dist /packages

RUN pip install --find-links=/packages copyxnat

ENTRYPOINT ["copyxnat --cache-dir /copyxnat"]

CMD ["--help"]

VOLUME ["/copyxnat"]
