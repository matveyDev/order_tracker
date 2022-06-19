#!/usr/bin/env bash

sleep 10

alembic revision --autogenerate -m 'first'

alembic upgrade head

python3 app.py
