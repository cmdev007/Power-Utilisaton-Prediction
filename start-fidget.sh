#!/bin/bash
cd backend/power/
rm -rf LKEY.txt
python3.8 runner.py&
python3.8 watchman.py&
cd ../../
python3.8 manage.py runserver
