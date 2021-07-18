#!/bin/bash
pkill python3.8

cd backend/power/linearRegression/
rm -rf LKEY.txt
python3.8 runner.py&
python3.8 watchman.py&
cd ../../../

cd backend/power/prototype_1/
rm -rf LKEY.txt
python3.8 runner.py
python3.8 watchman.py&
cd ../../../

cd backend/power/prototype_2/
rm -rf LKEY.txt
python3.8 runner.py
python3.8 watchman.py&  
cd ../../../

python3.8 manage.py runserver
