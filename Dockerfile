# We will install our software on Alpine Linux
FROM python:3.7-alpine

# User arguments
ARG NB_USER=amit
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
ENV PYTHONPATH /usr/lib/python3.7/site-packages

USER root

# Make a user and Install stuff
RUN adduser -D -u ${NB_UID} -h ${HOME} ${NB_USER} && \
    apk add --no-cache zeromq && \
    apk add --no-cache --virtual build-dependencies bash git gcc g++ \
        python3-dev ca-certificates libstdc++ zeromq-dev curl freetype-dev \
         libpng-dev && \
    apk add --no-cache --virtual test-dependencies ncdu && \
    apk add --no-cache \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
        hdf5 openblas py3-numpy py3-pandas py3-h5py py3-matplotlib && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install --no-cache-dir ipympl==0.3.3 pyhull==2015.2.1 && \
    cd ${HOME} && \
    git clone https://github.com/amit112amit/opsresults.git && \
    mv ${HOME}/opsresults/* ${HOME} && \
    rm -rf ${HOME}/opsresults && \
    bash ${HOME}/getdata && \
    rm -rf /usr/local/share/.cache && \
    apk del build-dependencies && \
    chown -R ${NB_UID} ${HOME}

USER ${NB_USER}

WORKDIR ${HOME}