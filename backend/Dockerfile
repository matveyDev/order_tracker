FROM python:3.10.5

WORKDIR /backend

COPY /requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN export FLASK_APP=app

RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
