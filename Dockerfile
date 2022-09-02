# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /bs

COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "python3", "better-starboard.py"]