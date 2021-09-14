# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt update -y && apt upgrade -y && apt install curl -y && pip3 install -r requirements.txt

COPY . .

CMD [ "python3",  "datapull.py"] 

