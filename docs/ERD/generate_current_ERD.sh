#!/usr/bin/env bash

FILENAME=${PWD}/current.pdf

cd $(git rev-parse --show-toplevel)
python manage.py graph_models funding institution project dashboard users system | dot -Tpdf -o ${FILENAME}
