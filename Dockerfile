FROM python:3

RUN git clone --depth=1 https://github.com/Bash-it/bash-it.git ~/.bash_it && \
  bash ~/.bash_it/install.sh --silent

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - && \
  apt-get upgrade -y && \
  apt-get install -y nodejs texlive-latex-extra texlive-xetex && \
  rm -rf /var/lib/apt/lists/*


# Install local ds_toolbox code
USER root
COPY /bin  /app
COPY /config /app
COPY README.md /app
COPY  requirements.txt /app
COPY setup.py /app
COPY ds_toolbox /app
WORKDIR /app
RUN python3 -m pip install /app --no-deps

# Install all python packages from requirements and install and enable jupyterlab extensions
RUN pip install --upgrade pip && \
  pip install --upgrade -r requirements.txt && \
  jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    @jupyterlab/latex \
    @jupyterlab/toc \
    @jupyterlab/plotly-extension \
    jupyterlab-spreadsheet


# Scripts to launch jupyterlab
COPY bin/entrypoint.sh /usr/local/bin/
COPY config/ /root/.jupyter/

EXPOSE 8888
VOLUME /notebooks
WORKDIR /notebooks
ENTRYPOINT ["entrypoint.sh"]