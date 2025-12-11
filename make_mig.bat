@echo off
python manage.py makemigrations 2>&1 >migrations_output.txt
type migrations_output.txt
