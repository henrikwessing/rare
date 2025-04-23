FROM 34334:base
# Install necessary packages and FRR
RUN apk add --no-cache nano tini frr frr-doc frr-pythontools

# Create a directory for FRR configuration
RUN mkdir -p /etc/frr
RUN mkdir -p /var/run/frr
RUN chown -R frr:frr /etc/frr /var/run/frr


#EXPOSE 179 2601 2604

COPY daemons /etc/frr/daemons
COPY ospfd.conf /etc/frr/ospfd.conf
COPY zebra*.conf /etc/frr/
COPY ripd*.conf /etc/frr/

RUN chown -R frr:frr /etc/frr /var/run/frr


ADD supervisor_router.conf /etc/supervisor/conf.d/routers.conf 
#ENTRYPOINT ["/sbin/tini", "--"]
# Start FRR
COPY docker-start /usr/lib/frr/docker-start
RUN chmod 755 /usr/lib/frr/docker-start
#USER frr
#CMD ["/usr/bin/supervisor"]
CMD ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]
#CMD ["/usr/lib/frr/docker-start"]


#install vrrpd, lldpd and quagga
#RUN apt-get install -y lldpd 
#RUN apt-get install -y frr
#RUN apt-get install -y openssh-server
#RUN apt-get install -y geany nano mousepad
#RUN apk add --no-cache lldpd frr openssh-server geany nano frr-pythontools

#add the quagga scripts
#USER frr
#COPY daemons /etc/frr/daemons#
#COPY ospfd.conf /etc/frr/ospfd.conf
#COPY zebra*.conf /etc/frr/
#COPY ripd*.conf /etc/frr/
#USER root
#RUN rc-update add frr default || echo "frr service not found"
#ADD sshd_config /etc/ssh/sshd_config

#add supervisord script and startup script and disable initial dhclient
#ADD start_vrrpd.py /start_vrrpd.py
#ADD supervisor_vrrpd.conf /etc/supervisor/conf.d/supervisor_vrrpd.conf
#RUN touch /home/cybertek/.XAuthority
#RUN rm -f /etc/supervisor/conf.d/supervisor_dhclient.conf
#CMD sysctl -w net.ipv4.ip_forward=1
#CMD ["rc-service", "frr", "start"]
