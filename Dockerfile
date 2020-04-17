FROM python:3

ADD compareSimilarities.py /

RUN pip install nltk

RUN pip install pandas

RUN pip install numpy

CMD [ "python", "./compareSimilarities.py" ]