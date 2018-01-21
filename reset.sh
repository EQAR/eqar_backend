#!/usr/bin/env bash
rm ./*/migrations/00*.py
rm ./*/migrations/00*.pyc

python ./manage.py flush
python ./manage.py makemigrations
python ./manage.py migrate