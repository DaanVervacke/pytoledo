FROM python:latest

LABEL Maintainer="RobinDBL"

WORKDIR /user/app

COPY * /user/app/

RUN pip3 install -r requirements.txt

CMD [ "python", "main.py" ]