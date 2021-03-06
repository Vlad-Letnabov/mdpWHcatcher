FROM ubuntu:18.04

MAINTAINER Your Name "youremail@domain.tld"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN python3 -m pip install -r requirements.txt

COPY . /app

#ENTRYPOINT [ "python3" ]

CMD [ "gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "-m", "007", "wsgi:app" ]
