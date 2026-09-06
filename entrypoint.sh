#!/bin/sh


pipenv run migrate

figlet -ct "Run app server"
pipenv run server