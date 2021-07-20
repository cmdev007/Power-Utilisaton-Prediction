#!/bin/bash
pkill python3.8

cd backend/power/
python3.8 watchman.py&

cd ../..
python3.8 manage.py runserver