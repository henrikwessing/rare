ARG VERSION="11"
FROM debian:${VERSION}
ARG VERSION
RUN apt-get update && apt-get  -y upgrade
RUN apt-get install -y curl gpg make nano procps git
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN echo "deb http://download.opensuse.org/repositories/home:/p4lang/Debian_${VERSION}/ /" | tee /etc/apt/sources.list.d/home:p4lang.list
RUN curl -fsSL "https://download.opensuse.org/repositories/home:p4lang/Debian_${VERSION}/Release.key" | gpg --dearmor | tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null
RUN apt-get update
RUN apt-get -y install p4lang-bmv2 p4lang-p4c wget default-jre
RUN apt-get install python3-pip -y
RUN git clone https://github.com/rare-freertr/RARE-bmv2.git /rare-bmv2
RUN pip install grpcio protobuf p4runtime
# Prepare FreeRtr (includes P4Runtime code)
RUN mkdir /freertr
RUN mkdir /p4
RUN wget http://www.freertr.org/rtr.jar -O /freertr/rtr.jar
RUN cd /rare-bmv2/02-PE-labs/p4src && p4c --target bmv2 --arch v1model --std p4-16 router.p4 -v 
COPY entrypoint.sh /p4/entrypoint.sh
WORKDIR /p4
RUN chmod +x /p4/entrypoint.sh

ENTRYPOINT ["/p4/entrypoint.sh"]
#CMD ["bash"]
#COPY *.p4 script_translate.sh script_install.sh ./
