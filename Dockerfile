FROM python:3.8-buster

# Install text editor in order to be able to debug in the container if necessary
RUN apt-get update && apt-get -y install vim

# Install python test libs (testing framework), pytest-cov (test coverage), pycodestyle
RUN python3 -m pip install pycodestyle pytest pytest-cov


COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt \
    && rm -f requirements.txt \
    && python3 -m pip freeze --all > all-dependencies.txt \
    && cat all-dependencies.txt


ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
    wget \
    bzip2 \
    ca-certificates \
    sudo \
    curl \
    locales \
    fonts-liberation \
    # run-one \ -> not found
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install NODE JS necessary to labextensions
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash
RUN apt-get install nodejs
RUN node -v
RUN npm -v

# Without following line, impossible to set LC_ALL=en_US.UTF-8
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Configure environment
ENV SHELL=/bin/bash \
    NB_USER="jovyan" \
    NB_UID="1000" \
    NB_GID="100" \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    HOME=/home/jovyan


# Enable prompt color in the skeleton .bashrc before creating the default NB_USER
RUN sed -i 's/^#force_color_prompt=yes/force_color_prompt=yes/' /etc/skel/.bashrc

# Create user jovyan
RUN useradd --create-home --no-log-init --uid 1000 -r -g users jovyan
USER jovyan
WORKDIR /home/jovyan

# Creation of folder shared in /home/jovyan/work
# (otherwise, folder is created when volume is mounted, and then jovyan has no write access to it)
RUN mkdir /home/jovyan/work \
    && mkdir /home/jovyan/work/shared
USER root

# https://github.com/krallin/tini
RUN mkdir -p /scripts \
    && wget https://github.com/krallin/tini/releases/download/v0.18.0/tini -P /scripts \
    && chmod +x /scripts/tini

EXPOSE 8888

# Configure container startup
ENTRYPOINT ["/scripts/tini", "-g", "--"]
CMD ["start-notebook.sh"]
# https://github.com/jupyter/docker-stacks/tree/master/base-notebook. No tag...
RUN wget https://raw.github.com/jupyter/docker-stacks/master/base-notebook/start.sh -P /usr/local/bin \
    && wget https://raw.github.com/jupyter/docker-stacks/master/base-notebook/start-notebook.sh -P /usr/local/bin \
    && wget https://raw.github.com/jupyter/docker-stacks/master/base-notebook/start-singleuser.sh -P /usr/local/bin \
    && chmod a+x /usr/local/bin/start.sh /usr/local/bin/start-notebook.sh /usr/local/bin/start-singleuser.sh \
    && wget https://raw.github.com/jupyter/docker-stacks/master/base-notebook/jupyter_notebook_config.py -P /etc/jupyter


# Install local ds_toolbox code
USER root
COPY . /app
WORKDIR /app
RUN python3 -m pip install /app --no-deps


# Following command are to use plotly in jupyterlab : https://plot.ly/python/getting-started/
# and add jupyterlab extensions
RUN export NODE_OPTIONS=--max-old-space-size=4096
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@1.1 --no-build
RUN jupyter labextension install @jupyterlab/toc --no-build
RUN jupyter labextension install jupyterlab-plotly@1.5.4 --no-build
RUN jupyter labextension install plotlywidget@1.5.4 --no-build
RUN jupyter lab build

WORKDIR /home/jovyan/work
USER root