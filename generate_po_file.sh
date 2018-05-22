#!/bin/bash

python manage.py dumpdata institution --format=json --indent=2 | sed 's/[{},]/\n/g' | awk '/name/ {print "_("substr($0, 12, length($0) - 12)")"}' > institutions_to_translate.py
python manage.py makemessages -l cy
rm institutions_to_translate.py
