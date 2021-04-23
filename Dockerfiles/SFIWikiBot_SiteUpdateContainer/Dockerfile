FROM mtmosier/sfiwikibot_base:0.3

LABEL maintainer="mtmosier@gmail.com"
LABEL version="0.3.5"

ENV HOME /root

COPY --chown=app:app scripts /home/app/scripts
RUN mkdir /home/app/SFIWikiBot
COPY --chown=app:app setup.py /home/app/SFIWikiBot/
COPY --chown=app:app SFIWikiBotLib /home/app/SFIWikiBot/SFIWikiBotLib
RUN chown -R app:app /home/app
RUN chown -R app:app /home/app
RUN chmod -R +r,og-w /home/app
RUN chmod -R u+x /home/app/scripts/*

RUN chown -R root:app /tmp
RUN chmod -R +r,ug+w /tmp
RUN find /tmp -type d -print0 | xargs -0 chmod g+s

RUN mkdir /etc/sfiWikiBot
ADD Dockerfiles/SFIWikiBot_SiteUpdateContainer/settings.ini /etc/sfiWikiBot/settings.ini
RUN chown -R root:app /etc/sfiWikiBot
RUN chmod -R ug+rw /etc/sfiWikiBot

WORKDIR /home/app/SFIWikiBot
RUN python3 setup.py install

RUN rm -rf /home/app/SFIWikiBot/build

WORKDIR /home/app

# Run the update wiki content script as a one-shot
CMD ["/home/app/scripts/updateWikiContent.sh"]
