FROM jupyter/scipy-notebook
USER root

# Install pandoc with latex integration to perform docx and pdf export
RUN apt -qq update \
 && apt install -yq --no-install-recommends \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
 && apt clean && rm -rf /var/lib/apt/lists/*

# Install tensorflow
RUN pip install --quiet --no-cache-dir \
    'tensorflow==2.2.0' && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Install pystan and fbprophet(fbprojet requires pystan already installed)
RUN python3 -m pip install pystan
RUN python3 -m pip install fbprophet

# Install local ds_toolbox code
COPY . /app
WORKDIR /app
RUN python3 -m pip install /app --no-deps


# Install other DataScience packages
RUN pip install --upgrade pip && \
  pip install --upgrade -r requirements.txt


# Install other jupyterlab extensions
RUN jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    @jupyterlab/latex \
    @ijmbarr/jupyterlab_spellchecker \
    @jupyterlab/toc \
    @jupyterlab/geojson-extension \
    @lckr/jupyterlab_variableinspector \
    @jupyter-voila/jupyterlab-preview \
    jupyterlab-spreadsheet \
    jupyterlab-plotly \
    plotlywidget \
    jupyterlab-drawio \
    jupyter-matplotlib \
    jupyterlab-datawidgets \
    jupyterlab-topbar-extension \
    jupyterlab-system-monitor \
    jupyterlab-topbar-text \
    jupyterlab-logout \
    jupyterlab-theme-toggle \
    jupyterlab_commands



# Run Environment
COPY bin/entrypoint.sh /usr/local/bin/
COPY config/ /root/.jupyter/
EXPOSE 8888
VOLUME /notebooks
WORKDIR /notebooks
ENTRYPOINT ["entrypoint.sh"]
