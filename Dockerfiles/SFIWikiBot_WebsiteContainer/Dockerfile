FROM mtmosier/sfiwikibot_base:0.3

LABEL maintainer="mtmosier@gmail.com"
LABEL version="0.4.5"

ENV HOME /root

COPY --chown=app:app webapp /home/app/webapp
COPY --chown=app:app scripts /home/app/scripts
RUN mkdir /home/app/SFIWikiBot
COPY --chown=app:app setup.py /home/app/SFIWikiBot/
COPY --chown=app:app SFIWikiBotLib /home/app/SFIWikiBot/SFIWikiBotLib
RUN chown -R app:app /home/app
RUN chown -R app:app /home/app
RUN chmod -R +r,og-w /home/app
RUN chmod -R u+x /home/app/scripts/*

RUN rm /etc/nginx/sites-enabled/default
ADD Dockerfiles/SFIWikiBot_WebsiteContainer/webapp.conf /etc/nginx/sites-enabled/webapp.conf

RUN mkdir /etc/sfiWikiBot
ADD Dockerfiles/SFIWikiBot_WebsiteContainer/settings.ini /etc/sfiWikiBot/settings.ini
RUN chown -R root:app /etc/sfiWikiBot
RUN chmod -R ug+rw /etc/sfiWikiBot

RUN chown -R root:app /tmp
RUN chmod -R +r,ug+w /tmp
RUN find /tmp -type d -print0 | xargs -0 chmod g+s

ADD Dockerfiles/SFIWikiBot_WebsiteContainer/sfiWikiBotEnvList.conf /etc/nginx/main.d/sfiWikiBotEnvList.conf

RUN mkdir /etc/service/sfiWikiBotInit
ADD Dockerfiles/SFIWikiBot_WebsiteContainer/sfiWikiBotInit.sh /etc/service/sfiWikiBotInit/run
RUN chmod +x /etc/service/sfiWikiBotInit/run

ADD Dockerfiles/SFIWikiBot_WebsiteContainer/crontab /root/crontab
RUN crontab /root/crontab

WORKDIR /home/app/SFIWikiBot
RUN python3 setup.py install

RUN rm -rf /home/app/SFIWikiBot/build
RUN rm -f /etc/service/nginx/down

WORKDIR /home/app

EXPOSE 80

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]
