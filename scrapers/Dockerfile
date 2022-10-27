FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY earthchem.py earthchem.py
COPY hydroshare.py hydroshare.py

CMD ["python3"]