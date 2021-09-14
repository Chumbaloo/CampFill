FROM python:3.9-slim-buster
WORKDIR /app
COPY . .
RUN apt update -y && apt upgrade -y && apt install curl -y && pip3 install -r requirements.txt
CMD [ "python3",  "datapull.py"] 
