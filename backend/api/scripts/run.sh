#!/bin/bash

cd ../backend

python3 manage.py makemigrations
python3 manage.py migrate
# Qcluster is for django_Q (Work in progress)
# python3 manage.py qcluster
python3 manage.py runserver 0.0.0.0:8000