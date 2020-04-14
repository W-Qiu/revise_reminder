###############################################################
# 1st stage, install all dependencies
###############################################################
FROM python:3.7.6-slim AS builder1

WORKDIR /usr/src/django

# extra dependency for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# install dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# download spacy model
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download en_core_web_lg

###############################################################
# 2nd stage
###############################################################
FROM builder1 as builder2

# copy project
COPY . .