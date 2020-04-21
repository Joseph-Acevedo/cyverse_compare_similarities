FROM python:3

RUN mkdir /work

ADD compareSimilarities.py /work/

RUN pip install nltk

RUN pip install pandas

RUN pip install numpy

RUN pip install spacy

CMD [ "python", "work/compareSimilarities.py" ]
