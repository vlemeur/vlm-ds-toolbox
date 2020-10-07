import logging
from math import ceil

import pandas as pd
from sklearn.neighbors import KernelDensity
import plotly.graph_objects as go
import numpy as np

logger = logging.getLogger(__name__)


def plot(traces, show=True, **kwargs):
    """
    General plot functions used to plot any plotly list of traces.

    :param traces: list of plotly traces to plot
    :type traces: list

    :param show: Boolean controlling whether or not to plot the curves
    :type show: bool, optional

    :param kwargs: optional arguments used in plot functions.
    Possible kwargs are :
    - x_axis_name string representing name of x axis
    - y_axis_name string representing name of y axis
    - x_min float value or string date representing minimal value to show along x_axis
    - x_max float value or string date representing maximal value to show along x_axis
    - y_min float value representing minimal value to show along y_axis
    - y_max float value  representing maximal value to show along y_axis
    - title tile of the graph
    - template string indicating plotly graph template to use. Possible choices are :
            "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
            See https://plot.ly/python/templates for more informations

    :return: plotly figure object
    """
    x_axis_name = kwargs.pop('x_axis_name', None)
    y_axis_name = kwargs.pop('y_axis_name', None)
    template = kwargs.pop('template', 'plotly_dark')
    widget = kwargs.pop('widget', False)

    fig = go.Figure()
    for trace in traces:
        fig.add_trace(trace)

    props = {}
    for arg_name in ['x_min', 'x_max', 'y_min', 'y_max']:
        props[arg_name] = kwargs[arg_name] if arg_name in kwargs else None

    fig.update_layout(
        title=kwargs['title'] if 'title' in kwargs else '',
        xaxis={'title': x_axis_name,
               'range': [props['x_min'], props['x_max']]},
        yaxis={'title': y_axis_name,
               'range': [props['y_min'], props['y_max']]},
        showlegend=True,
        legend=dict(x=-0.1, y=1.1, bgcolor='rgba(0,0,0,0)'),  # use of rgba to make rectangle transparent
        legend_orientation="h",
        template=template
    )

    if widget:
        return go.FigureWidget(fig)
    else:
        if show is True:
            fig.show()
        return fig


def plot_evolution(keys, df, show=True, additional_traces=None, webgl=False, **kwargs):
    """
    Plots time evolution of input keys contained in df and add optional additional traces.

    :param keys: list of quantities names corresponding to df pandas DataFrame columns names
    :type keys: list

    :param df: pandas DataFrame indexed by string date containing keys values
    :type df: pandas DataFrame

    :param show: Boolean controlling whether or not to plot the curves
    :type show: bool, optional

    :param additional_traces: list of plotly traces to add to current plot
    :type additional_traces: list, optional

    :param webgl: Boolean controlling whether or not to use webgl plots
    :type webgl: bool, optional

    :param kwargs: optional arguments used in plot functions.
    Possible kwargs are :
    - colors: list of string relative to curves colors (ex: colors= ['red', 'blue'])
    - names: list of string representing different curves names which will appear in legend
    (ex: names=['PACT1', 'PCS600'])
    - modes: list of curves string modes to use. Possible choices are 'lines', 'markers', 'lines+markers' (ex:
    modes = ['lines', 'lines'])
    - x_axis_name string representing name of x axis
    - y_axis_name string representing name of y axis
    - x_min float value or string date representing minimal value to show along x_axis
    - x_max float value or string date representing maximal value to show along x_axis
    - y_min float value representing minimal value to show along y_axis
    - y_max float value  representing maximal value to show along y_axis
    - bandwith dict containing up_value and down_value of band_with
    - target_number_points int representing number of points to plot
    - title tile of the graph
    - template string indicating plotly graph template to use. Possible choices are :
            "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
            See https://plot.ly/python/templates for more informations

    :return: plotly figure object
    """
    modes = kwargs.pop('modes', None)
    names = kwargs.pop('names', None)
    colors = kwargs.pop('colors', None)
    widget = kwargs.pop('widget', False)
    bandwith = kwargs.pop('bandwith', None)
    target_number_points = kwargs.pop('target_number_points', None)

    if 'x_axis_name' not in kwargs:
        kwargs['x_axis_name'] = 'Time'

    if target_number_points is not None:
        df = df[::ceil(len(df) / target_number_points)]

    plotting_function = go.Scattergl if webgl is True else go.Scatter

    traces = [
        plotting_function(
            x=df.index,
            y=df[key],
            name=names[ind] if names is not None else key,
            mode=modes[ind] if modes is not None else 'lines+markers',
            line={"color": colors[ind] if colors is not None else None}
        )
        for ind, key in enumerate(keys)
        if not df[key].isna().all()
    ]
    if additional_traces is not None:
        traces += additional_traces

    if bandwith is not None:
        if isinstance(bandwith, dict):
            traces += add_horizontal_bandwith(dict_bandwith=bandwith, x_values=df.index)
        elif isinstance(bandwith, list):
            for item in bandwith:
                traces += add_horizontal_bandwith(dict_bandwith=item, x_values=df.index)

    fig = plot(
        traces=traces,
        show=show,
        widget=widget,
        **kwargs
    )
    if widget:
        return fig
    else:
        return df


def plot_hist(keys, df, quantiles=None, show=True, **kwargs):
    """
    Plots histogram distribution of input keys contained in df and add optional vertical lines.

    :param keys: list of quantities names corresponding to df pandas DataFrame columns names
    :type keys: list

    :param df: pandas DataFrame indexed by string date containing keys values
    :type df: pandas DataFrame

    :param quantiles: list of float values between 0 and 1 representing quantiles to plot as a vertical bar (with
    values plotted in scientif notation). The quantiles will be ploted relative to first quantity of keys list.
    If unvalid_included=True, the quantiles will be ploted relative to valid quantities only.
    :type quantiles: list, optional

    :param show: Boolean controlling whether or not to plot the curves
    :type show: bool, optional

    :param kwargs: optional arguments used in plot functions.
    Possible kwargs are :
    - colors: list of string relative to curves colors (ex: colors= ['red', 'blue'])
    - names: list of string representing different curves names which will appear in legend
    (ex: names=['PACT1', 'PCS600'])
    - modes: list of curves string modes to use. Possible choices are 'lines', 'markers', 'lines+markers' (ex:
    modes = ['lines', 'lines'])
    - x_axis_name string representing name of x axis
    - y_axis_name string representing name of y axis
    - x_min float value or string date representing minimal value to show along x_axis
    - x_max float value or string date representing maximal value to show along x_axis
    - y_min float value representing minimal value to show along y_axis
    - y_max float value  representing maximal value to show along y_axis
    - title tile of the graph
    - target_number_points int representing number of points to plot
    - nbinsx int representing the number of histograms bars to use
    - template string indicating plotly graph template to use. Possible choices are :
            "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
            See https://plot.ly/python/templates for more informations

    :return: plotly figure object
    """
    # No need to use webgl here because points are aggregated
    names = kwargs.pop('names', None)
    colors = kwargs.pop('colors', None)
    widget = kwargs.pop('widget', False)
    kernel_density = kwargs.pop('kernel_density', None)
    kernel_bandwith = kwargs.pop('kernel_bandwith', 0.75)
    target_number_points = kwargs.pop('target_number_points', None)
    nbinsx = kwargs.pop('nbinsx', None) if kernel_density is None else kwargs.pop('nbinsx', int(len(df) / 2))
    quantiles = quantiles if quantiles is not None else []

    if target_number_points is not None:
        df = df[::ceil(len(df) / target_number_points)]

    traces = [
        go.Histogram(
            x=df[key],
            name=names[ind] if names is not None else key,
            nbinsx=nbinsx,  # To specify the maximum number of bins
            marker={"color": colors[ind] if colors is not None else None},
            histnorm="probability density" if kernel_density is not None else None
        )
        for ind, key in enumerate(keys)
        if not df[key].isna().all()
    ]

    if 'y_axis_name' not in kwargs:
        kwargs['y_axis_name'] = 'Number of elements' if kernel_density is None else None

    if kernel_density is not None:
        for key in keys:
            log_dens = KernelDensity(
                kernel=kernel_density,
                bandwidth=kernel_bandwith
            ).fit(df[key].values[:, None]).score_samples(df[key].values[:, None])
            density_values =  np.exp(log_dens)
            dkernel = pd.DataFrame(data={key: df[key].values, 'density': density_values}).sort_values(by=key)
            traces.append(
                go.Scatter(
                    x=dkernel[key],
                    y=dkernel['density'],
                    name=key + ' ' + kernel_density + 'density',
                    mode='lines'
                )
            )

    fig = plot(
        traces=traces,
        show=False,
        widget=widget,
        **kwargs
    )

    fig.update_layout(
        barmode='stack',
        shapes=[
            go.layout.Shape(
                type="line",
                yref="paper",
                x0=df[keys[0]].quantile(quantile),  # quantiles only for first key
                y0=0,
                x1=df[keys[0]].quantile(quantile),
                y1=1
            )
            for quantile in quantiles
            if not df[keys[0]].isna().all()
        ],
        annotations=[
            dict(
                x=df[keys[0]].quantile(quantile),
                y=1,
                xref='x',
                yref='paper',
                xanchor='left',
                text='Q' + str(quantile) + ': ' + str(format(df[keys[0]].quantile(quantile), ".2e")),
                showarrow=False,
                arrowhead=0,
            )
            for quantile in quantiles
            if not df[keys[0]].isna().all()
        ]
    )
    if widget:
        return go.FigureWidget(fig)
    else:
        if show is True:
            fig.show()
        return df
    

def plot_xy(df, x_name, y_names, z_name=None, show=True, date_format='%Y-%m-%dT%H:%M:%SZ', webgl=False, **kwargs):
    """
    Plots evolution of one or several input keys (in y_names) regarding an other one (x_name).
    It is possible to add an extra quantity used as markers coloration (using z_name)
    It also returns the pandas DataFrame used to perform the plot.

    :param df: pandas DataFrame containing columns relative to y_names, x_name and optional z_name quantities.
    :type df: pandas.DataFrame

    :param x_name: string, relative to quantity, used as x abscissa and contained in df
    :type x_name: str

    :param y_names: list of strings relative to quantities used as y curves and contained in df
    :type y_names: list

    :param z_name: string relative to quantity, used as optional marker coloration and contained in df
    :type z_name: str, optional

    :param show: Boolean controlling whether or not to plot the curves
    :type show: bool, optional

    :param date_format: string which indicates date format
    :type date_format: str, optional

    :param webgl: Boolean controlling whether or not to use webgl plots
    :type webgl: bool, optional

    :param kwargs: optional arguments used in plot functions.
    Possible kwargs are :
    - colors: list of string relative to curves colors (ex: colors= ['red', 'blue'])
    - names: list of string representing different curves names which will appear in legend
    (ex: names=['PACT1', 'PCS600'])
    - modes: list of curves string modes to use. Possible choices are 'lines', 'markers', 'lines+markers' (ex:
    modes = ['lines', 'lines'])
    - x_axis_name string representing name of x axis
    - y_axis_name string representing name of y axis
    - x_min float value or string date representing minimal value to show along x_axis
    - x_max float value or string date representing maximal value to show along x_axis
    - y_min float value representing minimal value to show along y_axis
    - y_max float value  representing maximal value to show along y_axis
    - target_number_points int representing number of points to plot
    - title tile of the graph
    - template string indicating plotly graph template to use. Possible choices are :
            "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
            See https://plot.ly/python/templates for more informations

    :return: plotly figure object
    """

    plotting_function = go.Scattergl if webgl is True else go.Scatter

    colors = kwargs.pop('colors', None)
    modes = kwargs.pop('modes', None)
    names = kwargs.pop('names', None)
    widget = kwargs.pop('widget', False)
    target_number_points = kwargs.pop('target_number_points', None)

    if target_number_points is not None:
        df = df[::ceil(len(df) / target_number_points)]

    marker = dict(color=df[z_name],
                  colorscale='Jet',
                  colorbar=dict(title=z_name, len=0.8, lenmode='fraction'),
                  opacity=0.8) if z_name is not None else None
    traces = [
        plotting_function(
            x=df[x_name],
            y=df[y_name],
            name=names[ind] if names is not None else y_name,
            marker=marker,
            mode=modes[ind] if modes is not None else 'markers',
            line={"color": colors[ind] if colors is not None else None},
            hoverinfo='text',
            text=[
                x_name + ' : ' + str(round(df[x_name].iloc[ind], 2)) + '<br>' + y_name + ' : ' + str(
                    round(df[y_name].iloc[ind], 2)) + ('<br>' + z_name + ' : ' + str(
                        round(df[z_name].iloc[ind], 2)) if z_name is not None else '') + (
                        '<br>' + df.index[ind].strftime(date_format)
                        if isinstance(df.index, pd.core.indexes.datetimes.DatetimeIndex) else '')
                for ind in range(len(df))]
        )
        for ind, y_name in enumerate(y_names)
        if not df[y_name].isna().all()
    ]
    if 'y_axis_name' not in kwargs:
        if len(y_names) == 1:
            kwargs['y_axis_name'] = y_names[0]
        else:
            kwargs['y_axis_name'] = ''
    if 'x_axis_name' not in kwargs:
        kwargs['x_axis_name'] = x_name
    fig = plot(
        traces=traces,
        show=show,
        widget=widget,
        **kwargs
    )
    if widget:
        return fig
    else:
        return df


def plot_bar(keys, x, df, show=True, **kwargs):
    """
    Plots bar from input keys, a pandas DataFrame df and a list of names used in x used in x axis.

    :param keys: list of quantities names corresponding to df pandas DataFrame columns names
    :type keys: list

    :param x: list of strings names used for x axis bar legends. It must match df index
    :type x: list

    :param df: pandas DataFrame containing keys values indexed by input x list
    :type df: pandas DataFrame

    :param show: Boolean controlling whether or not to plot the curves
    :type show: bool, optional

    :param kwargs: optional arguments used in plot functions.
    Possible kwargs are :
    - colors: list of string relative to curves colors (ex: colors= ['red', 'blue'])
    - names: list of string representing different curves names which will appear in legend
    (ex: names=['PACT1', 'PCS600'])

    - x_axis_name string representing name of x axis
    - y_axis_name string representing name of y axis
    - x_min float value or string date representing minimal value to show along x_axis
    - x_max float value or string date representing maximal value to show along x_axis
    - y_min float value representing minimal value to show along y_axis
    - y_max float value  representing maximal value to show along y_axis
    - title tile of the graph
    - template string indicating plotly graph template to use. Possible choices are :
            "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
            See https://plot.ly/python/templates for more informations

    :return: plotly figure object
    """
    names = kwargs.pop('names', None)
    colors = kwargs.pop('colors', None)
    widget = kwargs.pop('widget', False)

    traces = [
        go.Bar(
            name=names[ind] if names is not None else key,
            x=x,
            y=df[key],
            marker_color=colors[ind] if colors is not None else None
        )
        for ind, key in enumerate(keys)

    ]
    fig = plot(
        traces=traces,
        show=show,
        widget=widget,
        **kwargs
    )
    if widget:
        return fig
    else:
        return df


def plot_pie_chart(keys, values, show=True, **kwargs):
    """
    Plots pie-charts from keys (list of string names) and associated list of values.

    :param keys: list of string names to use
    :type keys: list

    :param values: list of float values associated with list of string names
    :type values: list

    :param show: Boolean controlling whether or not to plot the curves
    :type show: bool, optional

    :param kwargs: optional arguments used in plot functions.
    Possible kwargs are :
    - colors: list of string relative to area colors (ex: colors= ['red', 'blue', 'orange'])
    - title tile of the graph
    - template string indicating plotly graph template to use. Possible choices are :
            "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
            See https://plot.ly/python/templates for more informations

    :return: plotly figure object
    """
    colors = kwargs.pop('colors', None)
    widget = kwargs.pop('widget', False)
    traces = [
        go.Pie(
            labels=keys,
            values=values,
            marker=dict(colors=colors if colors is not None else None)
        )
    ]
    fig = plot(
        traces=traces,
        show=show,
        widget=widget,
        **kwargs
    )
    if widget:
        return fig
    else:
        return values


def add_horizontal_bandwith(dict_bandwith, x_values):
    return [
        go.Scatter(
            x=x_values,
            y=[dict_bandwith['up_value']] * len(x_values),
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(0,0,0,0)'),
            fill='none',
            showlegend=False
        ),
        go.Scatter(
            x=x_values,
            y=[dict_bandwith['down_value']] * len(x_values),
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(0,0,0,0)'),
            fill='tonexty',
            showlegend=False
        )
    ]