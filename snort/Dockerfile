FROM debian:11
# Install general prerequisites
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install \
                                       openssh-server \    
                                       ethtool \           
        wget \
        build-essential \
        libpcap-dev \
        libpcre3-dev \
        libdumbnet-dev \
        zlib1g-dev \
        liblzma-dev \
        openssl \
        libssl-dev \
	nano 
 
 
# Install DAQ prerequisites
RUN apt-get -y install \
                                       bison \
                                       flex \
                                      pkg-config \
                                       luajit
 
RUN usermod -p '$y$j9T$U8Hk9xud8LdTgUX68Z7lx.$kW2qyUmQDuzM9tIBISwbaIVFC9wSdh05ZuzsnSOm9E0' root
RUN useradd -d /home/cybertek -m -p "$(openssl passwd -1 34334)" -s /bin/bash cybertek -G sudo
RUN mkdir /home/cybertek/snort_src
 
 
WORKDIR /home/cybertek/snort_src
 
# Install DAQ
ENV DAQ_VERSION=2.0.7
RUN wget https://www.snort.org/downloads/snort/daq-${DAQ_VERSION}.tar.gz \
    && tar xvfz daq-${DAQ_VERSION}.tar.gz \
    && cd daq-${DAQ_VERSION} \
    && ./configure && make && make install
    
 
ENV SNORT_VERSION=2.9.20
RUN wget https://www.snort.org/downloads/snort/snort-${SNORT_VERSION}.tar.gz \
    && tar xvfz snort-${SNORT_VERSION}.tar.gz \
    && cd snort-${SNORT_VERSION} \
    && ./configure --enable-sourcefire --disable-open-appid && make && make install
 
RUN ldconfig
RUN ln -s /usr/local/bin/snort /usr/bin/snort
 
RUN mkdir /etc/snort \
                             /etc/snort/rules \
                             /etc/snort/preproc_rules \
                             /etc/snort/etc \
                             /etc/snort/so_rules && \
    touch /etc/snort/rules/white_list.rules /etc/snort/rules/black_list.rules /etc/snort/rules/local.rules && \
    chmod -R 5775 /etc/snort && \
    mkdir /var/log/snort && \
    chmod -R 5775 /var/log/snort && \
    mkdir /usr/local/lib/snort_dynamicrules && \  
    chmod -R 5775 /usr/local/lib/snort_dynamicrules && \
    cp /home/cybertek/snort_src/snort-${SNORT_VERSION}/etc/*.conf /etc/snort/etc && \
    cp -v /home/cybertek/snort_src/snort-${SNORT_VERSION}/etc/*.map* /etc/snort/etc
    
 
ENV SNORT_RULES_SNAPSHOT=29200
ADD snortrules-snapshot-${SNORT_RULES_SNAPSHOT}.tar.gz /etc/snort
#RUN tar -xvf /etc/snort/snortrules-snapshot-${SNORT_RULES_SNAPSHOT}.tar.gz /etc/snort/
#RUN cp community-rules/* /etc/snort/rules 
 
 
WORKDIR /home/cybertek
 
# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    /home/cybertek/snort_src/*

