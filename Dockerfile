# syntax=docker/dockerfile:1

FROM --platform=linux/amd64 python:3.9

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt 
RUN wget https://stockfishchess.org/files/stockfish-10-linux.zip
RUN unzip stockfish-10-linux.zip
RUN chmod +x stockfish-10-linux/Linux/stockfish_10_x64

COPY . .

ENV PYTHONUNBUFFERED="true"

WORKDIR app

CMD ["gunicorn", "-b",  "0.0.0.0:5000", "main:app"]