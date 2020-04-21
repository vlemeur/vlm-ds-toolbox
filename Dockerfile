FROM python:3
USER root

RUN git clone --depth=1 https://github.com/Bash-it/bash-it.git ~/.bash_it && \
  bash ~/.bash_it/install.sh --silent

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - && \
  apt-get upgrade -y && \
  apt-get install -y nodejs texlive-latex-extra texlive-xetex && \
  rm -rf /var/lib/apt/lists/*

COPY ./config/scripts_bash/install_simulation_libs.sh ./
RUN bash ./install_simulation_libs.sh \
    && rm -f ./install_simulation_libs.sh

# Install pandoc with latex integration to perform docx and pdf export
RUN apt-get -qq update \
 && apt-get install -yq --no-install-recommends \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-generic-recommended \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install orca to perform png exports and psutil (which requires orca)
COPY ./config/scripts_bash/prepare_env_for_png_generation.sh prepare_env_for_png_generation.sh
RUN sh prepare_env_for_png_generation.sh && rm -f prepare_env_for_png_generation.sh

# Install local ds_toolbox code

COPY . /app
WORKDIR /app
RUN python3 -m pip install /app --no-deps

RUN pip install --upgrade pip && \
  pip install --upgrade -r requirements.txt && \
  jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    @jupyterlab/latex \
    @ijmbarr/jupyterlab_spellchecker \
    @jupyterlab/toc \
    @jupyterlab/geojson-extension \
    @lckr/jupyterlab_variableinspector \
    @jupyter-voila/jupyterlab-preview \
    jupyterlab-spreadsheet \
    jupyterlab-plotly \
    jupyterlab-drawio \
    jupyter-matplotlib \
    jupyterlab-datawidgets \
    jupyterlab-topbar-extension \
    jupyterlab-system-monitor \
    jupyterlab-topbar-text \
    jupyterlab-logout \
    jupyterlab-theme-toggle \
    jupyterlab_commands



COPY bin/entrypoint.sh /usr/local/bin/
COPY config/ /root/.jupyter/

EXPOSE 8888
VOLUME /notebooks
WORKDIR /notebooks
ENTRYPOINT ["entrypoint.sh"]