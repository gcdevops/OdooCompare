FROM ubuntu:18.04

ARG APP_ENV

ENV APP_ENV ${APP_ENV}
ENV FLASK_ENV ${APP_ENV}

# install python 3.7
RUN apt update  &&  apt install -y software-properties-common curl && \
add-apt-repository -y ppa:deadsnakes/ppa && \
apt install -y python3.7 && python3.7 --version && apt install -y python3-pip && \
python3.7 -m pip install pip

# install nginx web server
RUN apt update && \
apt install -y nginx && \
rm /etc/nginx/sites-available/default && \
rm /etc/nginx/sites-enabled/default

# set working directory
WORKDIR /home/root

# set shell to bash
SHELL ["/bin/bash", "-c"]


# copy dependencies and create virtual environment with them installed
COPY ./requirements.txt ./requirements.txt
RUN pip3 install virtualenv --upgrade && \
virtualenv -p /usr/bin/python3.7 venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
pip install gunicorn


COPY ./app.py ./app.py
COPY ./src ./src

# copy docker settings 
COPY  ./docker ./docker

# converting file from ms to unix format otherwise will fail on windows
RUN apt update && apt-get install -y dos2unix
RUN dos2unix docker/scripts/start.sh
RUN dos2unix docker/nginx/default

# make start up script executable
RUN chmod 777 docker/scripts/start.sh

ENTRYPOINT [ "/bin/bash", "docker/scripts/start.sh"]
EXPOSE 80
