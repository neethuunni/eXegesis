FROM ubuntu:14.04

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update && apt-get install -y \
	build-essential \
	python \
	python-dev \
	python-pip \
	libffi-dev \
	nginx \
	supervisor \
	mysql-server \
	libmysqlclient-dev \
	python-cairo \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN sudo pip install virtualenv

RUN mkdir -p /home/svg-parser/

WORKDIR /home/svg-parser/
ADD . /home/svg-parser/

RUN virtualenv -p /usr/bin/python2.7 /home/svg-parser/env

RUN /etc/init.d/mysql start && \
	mysql -u root -e "CREATE DATABASE svg_parser;" && \
	mysql -u root -e "CREATE USER 'Gokul'@'localhost' IDENTIFIED BY 'qburst@12';" && \
	mysql -u root -e "GRANT ALL PRIVILEGES ON * . * TO 'Gokul'@'localhost';" && \
	source /home/svg-parser/env/bin/activate && \
	pip install uwsgi && \
	pip install -r /home/svg-parser/requirements.txt && \
	python /home/svg-parser/svg_parser/manage.py makemigrations && \
	python /home/svg-parser/svg_parser/manage.py migrate && \
	echo "from django.contrib.auth.models import User; \
	User.objects.create_superuser('admin', 'gokulnath@qburst.com', 'password@12')" | \
	python /home/svg-parser/svg_parser/manage.py shell

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx-svgparser.conf /etc/nginx/sites-available/default
COPY supervisor-svgparser.conf /etc/supervisor/conf.d/

ADD startup.sh /home/svg-parser/startup.sh
RUN chmod +x /home/svg-parser/startup.sh
RUN echo "root:qburst" | chpasswd

EXPOSE 80
ENTRYPOINT ["/home/svg-parser/startup.sh"]
