FROM 34334:base

#RUN pip install scapy pysmbclient
#RUN apt-get install -y winbind dhcping nginx
#RUN apt-get install -y nano
RUN apk add nginx nano

#set dhclient.conf to be aggressive with dhcp requests
#RUN echo 'retry 10;' >> /etc/dhcp/dhclient.conf
#RUN echo 'timeout 10;' >> /etc/dhcp/dhclient.conf

#fixup nsswitch so we can resolve wins
#RUN sed 's/files dns/wins files dns/' /etc/nsswitch.conf >> /etc/nsswitch.conf
#RUN rc-update add nginx default
ADD start_vic.py /start_vic.py
ADD supervisor_vics.conf /etc/supervisor/conf.d/victims.conf 
ADD default.conf /etc/nginx/http.d/default.conf
RUN mkdir /var/www/html
ADD index.html /var/www/html/index.html
#RUN rc-service nginx reload

#add configs for supervisord
#ADD supervisor_vics.conf /etc/supervisor/conf.d/supervisor_vics.conf
CMD ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]




