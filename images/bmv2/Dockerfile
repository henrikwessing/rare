ARG VERSION="11"
FROM debian:${VERSION}.11
ARG VERSION
RUN apt-get update && apt-get  -y upgrade
RUN apt-get install -y curl gpg make nano procps
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN echo "deb http://download.opensuse.org/repositories/home:/p4lang/Debian_${VERSION}/ /" | tee /etc/apt/sources.list.d/home:p4lang.list
RUN curl -fsSL "https://download.opensuse.org/repositories/home:p4lang/Debian_${VERSION}/Release.key" | gpg --dearmor | tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null
RUN apt-get update
RUN apt-get -y install p4lang-bmv2 p4lang-p4c
RUN apt-get install python3-pip -y
RUN pip install grpcio protobuf p4runtime
RUN mkdir /p4
WORKDIR /p4
#COPY *.p4 script_translate.sh script_install.sh ./
