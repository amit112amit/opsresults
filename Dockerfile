# We will install our software on Alpine Linux
FROM python:3.7-alpine

# User arguments
ARG NB_USER=amit
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

# Make a user and Install stuff
RUN mkdir -p ${HOME} && \
    adduser -D -u ${NB_UID} ${NB_USER} && \
    chmod g+w /etc/passwd /etc/group && \
    apk add --no-cache zeromq && \
    apk add --no-cache --virtual build-dependencies \
	git python3-dev ca-certificates libstdc++ gcc g++ zeromq-dev curl && \
    apk add --no-cache --virtual test-dependencies bash ncdu && \
    apk add --no-cache --virtual node-dependencies \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
        nodejs npm && \
    apk add --no-cache \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
        hdf5 openblas py3-numpy py3-h5py py3-pandas && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install --no-cache-dir notebook==6.0.1 jupyter==1.0.0 jupyterlab==1.1.4 plotly==4.1.1 \
	ipywidgets==7.5.1 && \
    export NODE_OPTIONS=--max-old-space-size=4096 && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && \
    jupyter labextension install plotlywidget@1.1.1 --no-build && \
    jupyter labextension install jupyterlab-plotly@1.1.2 --no-build && \
    jupyter lab build && \
    unset NODE_OPTIONS && \
    cd ${HOME} && \
    git clone https://github.com/amit112amit/opsresults.git && \
    bash ${HOME}/opsresults/postBuild && \
    cp ${HOME}/opsresults/fix-permissions /usr/bin/fix-permission && \
    cp ${HOME}/opsresults/jupyter_notebook_config.py ${HOME}/.jupyter && \
    chown -R ${NB_USER}:${NB_USER} ${HOME}/.jupyter
    chmod -R 755 ${HOME}/.jupyter
    fix-permissions ${HOME} && \
    npm cache clean --force && \
    rm -rf /usr/local/share/.cache && \
    rm -rf /usr/local/share/jupyter/lab/staging && \
    apk del build-dependencies node-dependencies

WORKDIR ${HOME}/opsresults

EXPOSE 8888

USER ${NB_USER}
