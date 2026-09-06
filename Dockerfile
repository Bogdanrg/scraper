ARG PYTHON_VERSION
ARG BASE_IMAGE

FROM python:3.12.13 as base
WORKDIR /app

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

RUN pip install pipenv
RUN apt-get update --fix-missing && \
    apt-get install -y \
      wget \
      curl \
      gcc \
      nano \
      g++ \
      make \
      lsof \
      libpq-dev \
      libffi-dev \
      figlet \
      netcat-traditional

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv --clear
RUN pipenv sync

FROM base as release

COPY . .

RUN > .env
RUN chmod +x /app/entrypoint.sh