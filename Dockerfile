FROM python:latest

LABEL Maintainer="RobinDBL"

WORKDIR /user/app

ADD . /user/app/

RUN pip3 install -r requirements.txt

CMD [ "python", "webserver.py" ]