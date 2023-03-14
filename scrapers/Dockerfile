FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY discovery.py discovery.py
COPY earthchem.py earthchem.py
COPY hydroshare.py hydroshare.py
COPY repo_stats.py repo_stats.py

CMD ["python3"]
