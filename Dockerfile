FROM jupyter/scipy-notebook
USER root

# Install pandoc with latex integration to perform docx and pdf export
RUN apt -qq update \
 && apt install -yq --no-install-recommends \
    pandoc \
    texlive-xetex \
    curl \
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

# Install Julia kernel
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.5/julia-1.5.2-linux-x86_64.tar.gz
RUN tar -xvzf julia-1.5.2-linux-x86_64.tar.gz
RUN cp -r julia-1.5.2 /opt/
RUN ln -s /opt/julia-1.5.2/bin/julia /usr/local/bin/julia
RUN mkdir /.julia
COPY packages.jl /opt/packages.jl
RUN julia /opt/packages.jl
RUN julia -e "using Pkg; Pkg.add(\"IJulia\"); Pkg.build(\"IJulia\");"



# Install other jupyterlab extensions
RUN jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    @jupyterlab/latex \
    @ijmbarr/jupyterlab_spellchecker \
    @jupyterlab/toc \
    @jupyterlab/geojson-extension \
    @lckr/jupyterlab_variableinspector \
    @aquirdturtle/collapsible_headings \
    jupyterlab-execute-time \
    @jupyter-voila/jupyterlab-preview \
    spreadsheet-editor \
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
