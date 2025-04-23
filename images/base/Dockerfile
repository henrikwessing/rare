FROM alpine:3.20
#MAINTAINER 34334
#adding a label here so we can easily delete our containers
LABEL 34334=true

#ENV DEBIAN_FRONTEND noninteractive
#things that are nice to have on all images
#RUN sed -i -e 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.dotsrc\.org\/ubuntu/' /etc/apt/sources.list
RUN apk update && apk upgrade
RUN apk add --no-cache python3 nmap bash iptables supervisor shadow openssl openrc iproute2
RUN mkdir -p /run/openrc && touch /run/openrc/softlevel

#set root creds create cybertek user with same password
RUN addgroup sudo
RUN usermod -p '$y$j9T$U8Hk9xud8LdTgUX68Z7lx.$kW2qyUmQDuzM9tIBISwbaIVFC9wSdh05ZuzsnSOm9E0' root
RUN useradd -d /home/cybertek -m -p "$(openssl passwd -1 34334)" -s /bin/bash cybertek -G sudo

VOLUME [ “/sys/fs/cgroup” ]
#fix unnecessary errors down the line
#RUN update-locale

#install python dependencies
#RUN pip install netifaces

#create directory for child images to store configuration in
RUN  mkdir -p /var/log/supervisor && mkdir -p /etc/supervisor/conf.d

#supervisor base configuration
ADD supervisor.conf /etc/supervisor/supervisor.conf
#add conf for dhclient
ADD supervisor_dhclient.conf /etc/supervisor/conf.d/supervisor_dhclient.conf

# default command
CMD ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]


