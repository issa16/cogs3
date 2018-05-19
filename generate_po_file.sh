#!/bin/bash

python manage.py dumpdata institution | sed 's/[{},]/\n/g' | awk '/name/ {print "_(\"" substr($0, 10, length($0) - 10) "\")"}' > institutions_to_translate.py
python manage.py makemessages -l cy
rm institutions_to_translate.py
