FROM alpine:3.9

RUN apk add --update py3-pip

COPY compareSimilarities.py /usr/src/app/

CMD python3 /usr/src/app/compareSimilarities.py