FROM python:3.9-slim

ADD /packages /packages

RUN pip install --find-packages "/packages/*.whl"

ENTRYPOINT ["copyxnat"]

CMD ["--help"]

VOLUME ["/root/CopyXnat"]
