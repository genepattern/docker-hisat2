FROM ubuntu:16.04

RUN \
  sed -Ei 's/^# (deb.*xenial-backports.*)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y software-properties-common && \
  apt-get install -y autoconf automake byobu bzip2 curl gfortran git htop lzma man sudo unzip vim wget && \
  apt-get install -y libbz2-dev libcurl4-openssl-dev libgsl0-dev liblzma-dev libncurses5-dev libpcre3-dev \
    libreadline6-dev libssl-dev python-dev python-pip zlib1g-dev && \
  rm -rf /var/lib/apt/lists/*

#RUN wget ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat2/downloads/hisat2-2.1.0-Linux_x86_64.zip

RUN \
  wget -c ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat2/downloads/hisat2-2.1.0-source.zip && \
  unzip hisat2-2.1.0-source.zip && \
  cd hisat2-2.1.0 && \
  make && \
  cp hisat2* /usr/local/bin  && \
  rm /hisat2-2.1.0-source.zip

RUN    pip install awscli 

RUN apt-get update && apt-get -y install samtools=0.1.19-1ubuntu1  && apt-get clean
    
COPY Dockerfile /build/Dockerfile
COPY jobdef.json /build/jobdef.json
COPY common/container_scripts/runS3OnBatch.sh /usr/local/bin/runS3OnBatch.sh
COPY common/container_scripts/runLocal.sh /usr/local/bin/runLocal.sh
COPY runS3Batch_prerun_custom.sh /usr/local/bin/runS3Batch_prerun_custom.sh
COPY runS3Batch_postrun_custom.sh /usr/local/bin/runS3Batch_postrun_custom.sh
COPY extractIndexIfNecessary.py /usr/local/bin/extractIndexIfNecessary.py

ENV HISAT2_HOME /hisat2-2.1.0

RUN chmod ugo+x /usr/local/bin/runS3OnBatch.sh /usr/local/bin/runLocal.sh 

CMD ["/usr/local/bin/runS3OnBatch.sh" ]

