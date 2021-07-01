#!/bin/bash
cd backend/power/
python3.8 runner.py&
python3.8 watchman.py&
cd ../../
python3.8 manage.py runserver
