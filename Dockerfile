FROM python:3

RUN mkdir /work

ADD compareSimilarities.py /

RUN pip install nltk

RUN pip install pandas

RUN pip install numpy

RUN pip install spacy

CMD [ "python", "./compareSimilarities.py" ]
