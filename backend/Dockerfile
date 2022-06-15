FROM python:3.10.5

WORKDIR /app

COPY /requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN export FLASK_APP=main

CMD [ "python3", "main.py" ]
