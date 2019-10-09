# We will install our software on Alpine Linux
FROM python:3.7-alpine

# User arguments
ARG NB_USER=amit
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
ENV PYTHONPATH /usr/lib/python3.7/site-packages

# Make a user and Install stuff
RUN adduser -D -u ${NB_UID} ${NB_USER} -h ${HOME} && \
    apk add --no-cache zeromq && \
    apk add --no-cache --virtual build-dependencies bash \
        git python3-dev ca-certificates libstdc++ gcc g++ zeromq-dev curl && \
    apk add --no-cache --virtual test-dependencies ncdu && \
    apk add --no-cache --virtual node-dependencies \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
        nodejs npm && \
    apk add --no-cache \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
        hdf5 openblas py3-numpy py3-h5py py3-pandas && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install --no-cache-dir notebook==6.0.1 jupyterlab==1.1.4 \
        ipywidgets==7.5.1 pyhull==2015.2.1 ipympl==0.3.3 && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && \
    jupyter labextension install jupyter-matplotlib --no-build && \
    jupyter lab build && \
    cd ${HOME} && \
    git clone https://github.com/amit112amit/opsresults.git && \
    mv ${HOME}/opsresults/* ${HOME} && \
    rm -rf ${HOME}/opsresults && \
    bash ${HOME}/getdata && \
    chown -R ${NB_UID} ${HOME} && \
    npm cache clean --force && \
    rm -rf /usr/local/share/.cache && \
    rm -rf /usr/local/share/jupyter/lab/staging && \
    apk del build-dependencies node-dependencies test-dependencies

WORKDIR ${HOME}

EXPOSE 8888

USER ${NB_USER}
