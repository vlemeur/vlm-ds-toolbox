FROM python:3

RUN git clone --depth=1 https://github.com/Bash-it/bash-it.git ~/.bash_it && \
  bash ~/.bash_it/install.sh --silent

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - && \
  apt-get upgrade -y && \
  apt-get install -y nodejs texlive-latex-extra texlive-xetex && \
  rm -rf /var/lib/apt/lists/*


# Install local ds_toolbox code
USER root
COPY . /app
WORKDIR /app
RUN python3 -m pip install /app --no-deps

RUN pip install --upgrade pip && \
  pip install --upgrade -r requirements.txt && \
  jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    @jupyterlab/latex \
    @jupyterlab/toc \
    @jupyterlab/plotly-extension \
    jupyterlab-spreadsheet



COPY bin/entrypoint.sh /usr/local/bin/
COPY config/ /root/.jupyter/

EXPOSE 8888
VOLUME /notebooks
WORKDIR /notebooks
ENTRYPOINT ["entrypoint.sh"]