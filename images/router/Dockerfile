ARG VERSION="11"
FROM debian:${VERSION}
ARG VERSION
#Installing common utilities and dependencies
RUN apt-get update # && apt-get  -y upgrade
RUN apt-get install -y curl gpg make nano procps git
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
# Installing P4 Runtime, P4C and BMv2
RUN echo "deb http://download.opensuse.org/repositories/home:/p4lang/Debian_${VERSION}/ /" | tee /etc/apt/sources.list.d/home:p4lang.list
RUN curl -fsSL "https://download.opensuse.org/repositories/home:p4lang/Debian_${VERSION}/Release.key" | gpg --dearmor | tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null
RUN apt-get update
RUN apt-get -y install p4lang-bmv2 p4lang-p4c
RUN apt-get install python3-pip -y

# Installing RARE  p4 code and get the necessary parts - rest can be deleted
RUN apt-get update && apt-get install -y default-jre wget telnetd
RUN git clone https://github.com/rare-freertr/RARE-bmv2.git /rare-bmv2
RUN mkdir /p4
RUN cp /rare-bmv2/02-PE-labs/p4src/* /p4 -r
#RUN pip install grpcio protobuf p4runtime
# Prepare FreeRtr
RUN wget http://www.freertr.org/rtr.jar -O /p4/rtr.jar
RUN apt-get install -y supervisor
WORKDIR /p4
RUN cd /p4
RUN p4c --target bmv2 --arch v1model --std p4-16 router.p4 --p4runtime-files router.p4info.txt -o build
RUN apt-get install -y telnet telnetd
COPY router-hw.txt router-sw.txt /p4/
COPY cmd_bmv2.sh cmd_freertr.sh cmd_forwarder.sh /p4/
#create directory for child images to store configuration in
RUN  mkdir -p /var/log/supervisor && mkdir -p /etc/supervisor/conf.d

#supervisor base configuration
ADD supervisor.conf /etc/supervisor/supervisor.conf
#add conf for dhclient
ADD supervisor_dhclient.conf /etc/supervisor/conf.d/supervisor_dhclient.conf

# default command
CMD ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]
