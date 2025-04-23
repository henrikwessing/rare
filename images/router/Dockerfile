FROM debian:buster
MAINTAINER Rob Gil (rob@rem5.com)

ENV DEBIAN_FRONTEND noninteractive
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn

RUN apt-get update && \
    apt-get install -y nano libpcre3-dev apt-transport-https ca-certificates curl wget logrotate \
    libc-ares2 libjson-c3 vim procps libreadline7 gnupg2 lsb-release apt-utils \
    libprotobuf-c-dev protobuf-c-compiler tini supervisor  && rm -rf /var/lib/apt/lists/*

RUN curl -s https://deb.frrouting.org/frr/keys.asc | apt-key add -
#RUN echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) frr-stable | tee -a /etc/apt/sources.list.d/frr.list
RUN echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) frr-8 | tee -a /etc/apt/sources.list.d/frr.list

RUN apt-get update && \
    apt-get install -y frr frr-pythontools && \
    rm -rf /var/lib/apt/lists/*

# Own the config / PID files
RUN mv /etc/frr/daemons /etc/frr/daemons_original

COPY ospfd.conf /etc/frr/ospfd.conf
COPY zebra*.conf /etc/frr/
COPY ripd*.conf /etc/frr/
COPY daemons /etc/frr/


RUN mkdir -p /var/run/frr
RUN chown -R frr:frr /etc/frr /var/run/frr

# Simple init manager for reaping processes and forwarding signals
#ENTRYPOINT ["/usr/bin/tini", "--"]

# Default CMD starts watchfrr
COPY --chmod=0755 docker-start /usr/lib/frr/docker-start
#CMD ["/usr/lib/frr/docker-start"]
RUN  mkdir -p /var/log/supervisor && mkdir -p /etc/supervisor/conf.d

#supervisor base configuration
ADD supervisor.conf /etc/supervisor/supervisor.conf
#add conf for dhclient
ADD supervisor_dhclient.conf /etc/supervisor/conf.d/supervisor_dhclient.conf


CMD ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]

