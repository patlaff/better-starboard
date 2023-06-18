# syntax=docker/dockerfile:1

ARG BS_TOKEN

FROM python:3.10-buster

WORKDIR /bs

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./src/ .
RUN echo "BS_TOKEN=$BS_TOKEN" >> .env
RUN pip3 install -r requirements.txt

CMD ["python3", "better-starboard.py"]