ARG VERSION=11
# ========================
#       BUILD stage 
# ========================
FROM debian:$VERSION as build
ARG VERSION

#Installing common utilities and dependencies
RUN apt-get update 
RUN apt-get install -y curl gpg make nano procps git apt-transport-https ca-certificates
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN echo "deb http://download.opensuse.org/repositories/home:/p4lang/Debian_${VERSION}/ /" | tee /etc/apt/sources.list.d/home:p4lang.list
RUN curl -fsSL "https://download.opensuse.org/repositories/home:p4lang/Debian_${VERSION}/Release.key" | gpg --dearmor | tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null

# Installing P4 compiler
RUN apt-get update
RUN apt-get -y install p4lang-p4c
RUN apt-get install python3-pip -y
# Installing RARE  p4 code and get the necessary parts - rest can be deleted
RUN git clone https://github.com/rare-freertr/RARE-bmv2.git /rare-bmv2
RUN mkdir /p4
WORKDIR /p4
RUN cp /rare-bmv2/02-PE-labs/p4src/* /p4 -r
RUN cp /rare-bmv2/02-PE-labs/0000-topology-A/bin/pcapInt.bin /p4
# Compile P4 code - We do not need the compiler afterwards
RUN apt-get install -y build-essential libpcap-dev wget
RUN cd /p4
RUN p4c --target bmv2 --arch v1model --std p4-16 router.p4 --p4runtime-files router.p4info.txt -o build

# Prepare FreeRtr
RUN mkdir /p4/freertr
RUN cd /p4
RUN wget http://www.freertr.org/rtr.jar 
RUN wget http://www.freertr.org/rtr-$(uname -m).tgz -O rtr.tgz 
RUN tar -xvf rtr.tgz -C /p4/freertr

# ==================
#    RUNTIME stage
# ==================
FROM debian:$VERSION
ARG VERSION
# Prepare for installing p4-bmv2 for runtime
COPY --from=build /etc/apt/sources.list.d/home:p4lang.list /etc/apt/sources.list.d/
COPY --from=build /etc/apt/trusted.gpg.d/home_p4lang.gpg /etc/apt/trusted.gpg.d/home_p4lang.gpg
# Install java environment, p4 bmv2 runtime and misc
RUN apt-get update && apt-get install -y --no-install-recommends default-jre telnetd nano libpcap0.8 supervisor iproute2 telnet p4lang-bmv2 \
   && rm -rf /var/lib/apt/lists/*
# Copying compiled code and FreeRtr files from build
COPY --from=build /p4 /p4
COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /usr/local/include/ /usr/local/include/
ENV LD_LIBRARY_PATH=/usr/local/lib

# Adding the generic convenience commands
WORKDIR /p4
COPY cmd_freertr.sh cmd_forwarder.sh cmd_ctrlchannel.sh /p4/

# To keep container active - keep for now but probably irrelevant
RUN  mkdir -p /var/log/supervisor && mkdir -p /etc/supervisor/conf.d
ADD supervisor.conf /etc/supervisor/supervisor.conf
ADD supervisor_dhclient.conf /etc/supervisor/conf.d/supervisor_dhclient.conf
# Default command
CMD ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]
