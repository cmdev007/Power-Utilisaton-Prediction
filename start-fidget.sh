#!/bin/bash
cd backend/power/
python3.8 runner.py&
cd ../../
python manage.py runserver
