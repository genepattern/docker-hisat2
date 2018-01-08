# copyright 2017-2018 Regents of the University of California and the Broad Institute. All rights reserved.
FROM ubuntu:14.04

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

# get NBCI Toolkit
WORKDIR /tmp
RUN wget http://ftp-trace.ncbi.nlm.nih.gov/sra/ngs/1.3.0/ngs-sdk.1.3.0-linux.tar.gz && \
    tar xzvf ngs-sdk.1.3.0-linux.tar.gz

# Install hisat2
WORKDIR /tmp
RUN git clone https://github.com/infphilo/hisat2.git
WORKDIR /tmp/hisat2
RUN git checkout master

# Compile
RUN make USE_SRA=1 NCBI_NGS_DIR=/tmp/ngs-sdk.1.3.0-linux NCBI_VDB_DIR=/tmp/ngs-sdk.1.3.0-linux
RUN cp -p hisat2 hisat2-* /usr/local/bin

RUN    pip install awscli 

RUN apt-get update && apt-get -y install samtools=0.1.19-1  && apt-get clean

RUN cd / && \
    wget http://ftp-trace.ncbi.nlm.nih.gov/sra/ngs/1.3.0/ngs-sdk.1.3.0-linux.tar.gz && \
    tar xzvf ngs-sdk.1.3.0-linux.tar.gz && \
    export LD_LIBRARY_PATH=/ngs-sdk.1.3.0-linux/lib64:$LD_LIBRARY_PATH    

    
COPY Dockerfile /build/Dockerfile
COPY jobdef.json /build/jobdef.json
COPY common/container_scripts/runS3OnBatch.sh /usr/local/bin/runS3OnBatch.sh
COPY common/container_scripts/runLocal.sh /usr/local/bin/runLocal.sh
COPY runS3Batch_prerun_custom.sh /usr/local/bin/runS3Batch_prerun_custom.sh
COPY runS3Batch_postrun_custom.sh /usr/local/bin/runS3Batch_postrun_custom.sh
COPY extractIndexIfNecessary.py /usr/local/bin/extractIndexIfNecessary.py
COPY hisat_wrapper.py /usr/local/bin/hisat_wrapper.py
RUN cp -p /tmp/hisat2/hisat2_* /usr/local/bin
RUN cp -p /tmp/hisat2/extract*.py /usr/local/bin

ENV HISAT2_HOME /hisat2-2.1.0

RUN chmod ugo+x /usr/local/bin/runS3OnBatch.sh /usr/local/bin/runLocal.sh 

CMD ["/usr/local/bin/runS3OnBatch.sh" ]

