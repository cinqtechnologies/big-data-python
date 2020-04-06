FROM python:3

ADD irr.py /
ADD requirements.txt /
ADD Ativos.csv /

RUN pip install -r requirements.txt

CMD [ "python", "irr.py", "Ativos.csv" ]
