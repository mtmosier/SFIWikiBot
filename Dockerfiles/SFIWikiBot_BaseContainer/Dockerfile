FROM phusion/passenger-customizable:1.0.13

LABEL maintainer="mtmosier@gmail.com"
LABEL version="0.3"


# Set correct environment variables.
ENV HOME /root

RUN /pd_build/python.sh

RUN mkdir /home/app/webapp
COPY --chown=app:app requirements.txt /home/app/webapp/
RUN chown -R app:app /home/app/webapp

RUN apt-get update -y && apt-get upgrade -y -o Dpkg::Options::="--force-confold"
RUN apt-get install -y curl vim python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install --trusted-host pypi.python.org -r /home/app/webapp/requirements.txt

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN rm -f /home/app/webapp/requirements.txt

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]
