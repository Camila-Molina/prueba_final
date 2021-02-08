import urllib
import pandas as pd
import numpy as np
from datetime import datetime
from palettable.cartocolors import qualitative
import plotly.graph_objects as go
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
pd.options.mode.chained_assignment = None

external_stylesheets = ['https://fonts.googleapis.com/css?family=Open+Sans:300,400,700',
                        'https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

app.css.config.serve_locally = True
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally = True

application = app.server

app.title = 'Tracking R'

app.layout = html.Div([

    # location component used for switching between the
    # results page and the FAQ page
    dcc.Location(id='url', refresh=False),

    # contents of the selected page (either the results page or
    # the FAQ page depending on the user's selection)
    html.Div(id='page_content'),

])

# layout of results page
results_page = html.Div(children=[

    # title
    html.Div(children=[

        html.H1(children=['Tracking ', html.Span(children=['R'], style={'font-style': 'italic'})],
        style={'display': 'inline', 'font-size': '200%'}),

    ], style={'text-align': 'center', 'margin': '2vw 0vw 0vw 0vw'}),

    # subtitle
    html.H2(children=['Real-Time Estimates of the Effective Reproduction Rate (', html.Span(children=['R'],
    style={'font-style': 'italic'}), ' ) of COVID-19'], style={'text-align': 'center', 'font-size': '150%'}),

    # links
    html.Div(children=[

        html.A(children=['[FAQ]'], href='/FAQ', target='_blank', style={'display': 'inline',
        'margin':'0vw 0vw 0vw 0vw'}),

        html.A(children=['[Data]'], target='_blank', href='https://drive.google.com/open?id=1HWrq_gy_trT0_FyezDsLxCbpBbN4wamI',
        style={'display': 'inline', 'margin':'0vw 0vw 0vw 2vw'}),

        html.A(children=['[Code]'], target='_blank', href='https://drive.google.com/open?id=1TVNHlqmobn-cF1CxfbdwoCyaGk90aLEz',
        style={'display': 'inline', 'margin':'0vw 0vw 0vw 2vw'}),

        html.A(children=['[Paper]'], target='_blank', href='https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3581633', style={'display': 'inline',
        'margin':'0vw 0vw 0vw 2vw'}),

    ], style={'text-align': 'center'}),

    html.Div(children=[

        # dropdown
        html.Label(children=['Country / Region'], style={'margin': '4vw 0vw 0.3vw 0vw'}),

        html.Div(children=[

            dcc.Dropdown(id='selected_countries', multi=True, clearable=False),

        ], style={'width': '80%'}),

        # slider
        html.Label(children=['Average Serial Interval (Days)'], style={'margin': '2vw 0vw 1vw 0vw'}),

        html.Div(children=[

            dcc.Slider(id='selected_days', updatemode='drag'),

        ], style={'width': '80%', 'margin': '0vw 0vw 0vw -1vw'}),

        # checklist
        html.Label(children=['Credible Bounds'], style={'margin': '2vw 0vw 0.3vw 0vw'}),

        dcc.Checklist(id='selected_bounds', options=[{'label': '65% Credible Bounds', 'value': 'q65'},
        {'label': '95% Credible Bounds', 'value': 'q95'}], value=['q65', 'q95'],
        style={'font-size': '90%'}),

        # download
        html.Div(children=[
            
            html.A(children=['Download Estimates (CSV)'], target='_blank', href='https://drive.google.com/file/d/1upiT6JpXj0WCFYxl18a7osGD-igxzgJz/view?usp=sharing', style={'cursor': 'pointer'}),

        ], style={'margin': '2vw 0vw 0vw 0vw'}),

    ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin': '0vw 0vw 0vw 20vw', 'width': '18%'}),

    # graph
    html.Div(children=[

         dcc.Graph(id='line_chart', config={'displaylogo': False, 'responsive': True, 'autosizable': True,
        'scrollZoom': True, 'fillFrame': False, 'frameMargins': 0}, style={'width': '45vw', 'height': '22.5vw',
        'margin': '1vw 0vw 0vw 0vw', 'padding': '0'}),

    ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin': '0vw 0vw 0vw 0vw', 'width': '50%'}),

    # date
    html.Div(id='last_updated', style={'font-style': 'italic', 'font-size': '80%', 'margin': '3vw 0vw 0vw 73vw'}),

    # hidden div used for triggering the callbacks with no inputs
    html.Div(id='none', style={'display': 'none'}),

])

# layout of FAQ page
faq_page = html.Div(children=[

    # title
    html.H1(children=['Frequently Asked Questions (FAQs)'], style={'font-size': '200%'}),

    # first question
    html.Label(children=['1. How are the effective reproduction numbers calculated?'], style={'font-size': '110%', 'font-weight': '600', 'margin': '2vw 0vw 0vw 0vw'}),
    html.P(children=['The effective reproduction numbers are inferred from the growth rate of the number of infected individuals. First, we calculate the number of infected individuals from data on new cases. Then, we use statistical filtering techniques to obtain a “smoothed” version of the growth rate of the number of infected individuals. Finally, we use a formula given by standard epidemiological theory to infer the effective reproduction number. The full technical details are provided in the associated paper.']),

    # second question
    html.Label(children=['2. What is the source of the original data?'], style={'font-size': '110%', 'font-weight': '600', 'margin': '2vw 0vw 0vw 0vw'}),
    html.P(children=['The original data are collected by the John Hopkins CSSE team and are publicly available online (https://github.com/CSSEGISandData/COVID-19).']),

    # third question
    html.Label(children=['3. What are the known issues / limitations of the estimates?'], style={'font-size': '110%', 'font-weight': '600', 'margin': '2vw 0vw 0vw 0vw'}),
    html.P(children=['First, if new cases are reported with a delay, then our estimates will also be delayed. Second, if the fraction of detected COVID-19 cases changes rapidly over short windows of time, that will bias the estimates. Third, because of data limitations, we do not account for imported cases. Finally, the estimates may be less reliable when the number of new cases is very low (e.g., later on in the epidemic). For further discussion of these and some additional potential issues, please see the associated paper.']),

    # fourth question
    html.Label(children=['4. Are the estimated reproduction numbers accurate if not all cases of COVID-19 are detected?'], style={'font-size': '110%', 'font-weight': '600', 'margin': '2vw 0vw 0vw 0vw'}),
    html.P(children=['In the paper, we show theoretically that even if not all cases of COVID-19 are detected, the estimates remain valid if the percentage of detected cases is roughly constant (for example, 10% of the cases are detected). The estimates are also accurate under some other cases of mismeasurement. However, if the fraction of detected COVID-19 cases changes a lot over short windows of time, that will bias the estimates.']),

    # fifth question
    html.Label(children=['5. Are there any other dashboards that provide real-time estimates of the effective reproduction number?'], style={'font-size': '110%', 'font-weight': '600', 'margin': '2vw 0vw 0vw 0vw'}),
    html.P(children=['Yes – three that we are aware of are (i) https://cbdrh.github.io/ozcoviz/; (ii) rt.live; and (iii) https://epiforecasts.io/covid/posts/global/. We encourage the users to compare estimates across the different methods and dashboards. Averaging multiple estimates is much more likely to yield accurate estimates and reduce model uncertainty.']),

    # sixth question
    html.Label(children=['6. How should the "Average Serial Interval" be chosen?'], style={'font-size': '110%', 'font-weight': '600', 'margin': '2vw 0vw 0vw 0vw'}),
    html.P(children=['The serial number of a disease is the time between onset of symptoms in a case and onset of symptoms in his/her secondary cases. For COVID-19, the average serial interval is estimated to be around 4–8 days. In our baseline estimates, we use a serial interval of 7 days which yields estimates of the basic reproduction number that are consistent with the current consensus values.']),

    # secenth question
    html.Label(children=['7. How can I reach you?'], style={'font-size': '110%', 'font-weight': '600', 'margin': '2vw 0vw 0vw 0vw'}),
    html.P(children=['You can write an email to simas [dot] kucinskas [at] hu [dash] berlin [dot] de – all comments and suggestions are most welcome.']),


], style={'margin': '2vw 0vw 0vw 2vw'})

# callback for loading the data
@app.callback([Output('last_updated', 'children'), Output('selected_countries', 'options'),
               Output('selected_countries', 'value'), Output('selected_days', 'min'),
               Output('selected_days', 'max'), Output('selected_days', 'marks'),
               Output('selected_days', 'value')], [Input('none', 'children')])
def load_data(none):

    # load the data
    df = pd.read_csv('database.csv')

    # extract the date of the last update
    last_updated = 'Last updated on ' + pd.to_datetime(df['last_updated']).max().strftime(format='%d %B %Y')

    # extract the countries / regions
    countries = df['Country/Region'].sort_values().unique()

    # add the countries / regions as options
    # in the dropdown menu
    dropdown_options = [{'value': countries[0], 'label': countries[0]}]

    if len(countries) > 1:
        for j in range(1, len(countries)):
            dropdown_options.append({'value': countries[j], 'label': countries[j]})

    # use 'World' as the initial dropdown menu selection
    dropdown_value = ['World']

    # extract the number of days infectious
    days = df['days_infectious'].unique().astype(int)

    # use five equally spaced days as slider marks
    slider_options = dict(zip([str(days[i]) for i in range(0, len(days), int(len(days)/5))],
                     [str(days[i]) for i in range(0, len(days), int(len(days)/5))]))

    # use 7 as the initial slider selection
    slider_value = 7

    return [last_updated, dropdown_options, dropdown_value, days.min(), days.max(), slider_options, slider_value]

# callback for updating the line chart
@app.callback(Output('line_chart', 'figure'), [Input('selected_countries', 'value'),
               Input('selected_days', 'value'), Input('selected_bounds', 'value')])
def update_graph(countries, days, bounds):

    # if no countries have been selected,
    # display a warning message
    if countries == []:

        layout = dict(font=dict(family='Open Sans', color='#737373'), paper_bgcolor='white', plot_bgcolor='white',
        xaxis=dict(visible=False), yaxis=dict(visible=False), margin=dict(t=50, l=0, r=0, b=0, pad=0),
        showlegend=False)

        data = []

        data.append(go.Scatter(x=[1,2,3], y=[1,2,3], opacity=0, hoverinfo=None))
        data.append(go.Scatter(x=[2], y=[2], text='No data to display', mode='text', hoverinfo=None))

        figure = go.Figure(data=data, layout=layout).to_dict()

        return figure

    # if at least one country has been selected,
    # display the graph
    else:

        # extract the color palette
        col1 = qualitative.Vivid_10.hex_colors * 5
        col2 = ['rgba(' + str(x)[1:-1] + ', 0.12)' for x in list(qualitative.Vivid_10.colors)] * 5
        col3 = ['rgba(' + str(x)[1:-1] + ', 0.06)' for x in list(qualitative.Vivid_10.colors)] * 5

        # load the data
        df = pd.read_csv('data/database.csv')

        # format the date column
        df['Date'] = pd.to_datetime(df['Date'])

        # sort the data by country / region and by date
        df.sort_values(by=['Country/Region', 'Date'], inplace=True)
        df.reset_index(inplace=True, drop=True)

        # extract the selected countries / regions and the selected number of days infectious
        df = df[(df['Country/Region'].isin(countries)) & (df['days_infectious'] == int(days))]

        # extract the last value of R for each of the selected countries / regions
        # to be annotated on the chart
        dfl = df[['Country/Region', 'R']][df['Date'] == df['Date'].max()]
        dfl.sort_values(by='R', inplace=True)
        dfl.reset_index(inplace=True, drop=True)

        # if the annotations are too close to each other, add an offset
        dfl['P'] = dfl['R'] # initial annotations positions
        offset = (df['R'].quantile(0.95) - df['R'].quantile(0.05)) / 10

        for i in range(1, len(countries)):

            if abs(dfl['P'][i] - dfl['P'][i - 1]) < offset:

                dfl['P'][i] = dfl['P'][i - 1] + offset

        # create the chart annotations
        annotations = []

        for i in range(len(countries)):

            dfs = dfl[(dfl['Country/Region'] == countries[i])]

            annotations.append(dict(xref='paper', xanchor='left', x=1.01, y=dfs['P'].values[0], font=dict(color=col1[i]),
            text=format(dfs['R'].values[0],'.2f'), showarrow=False))

        # create the chart layout
        layout = dict(font=dict(family='Open Sans', color='#737373'), paper_bgcolor='white', plot_bgcolor='white',
        xaxis=dict(showgrid=False, zeroline=False, mirror=True, color='#737373', linecolor='#d9d9d9',
        tickformat='%d %b %y'), yaxis=dict(showgrid=False, zeroline=False, mirror=True, color='#737373',
        linecolor='#d9d9d9'), margin=dict(t=50, l=0, r=0, b=0, pad=0), annotations=annotations, showlegend=True)

        # create the chart traces
        data = []

        data.append(go.Scatter(x=list(df['Date']), y=[0]*len(df['Date']), mode='lines',
        line=dict(color='#737373', width=1, dash='dot'), hoverinfo='none', showlegend=False)),

        data.append(go.Scatter(x=list(df['Date']), y=[1]*len(df['Date']), mode='lines',
        line=dict(color='#737373', width=1, dash='dot'), hoverinfo='none', showlegend=False)),

        if 'q65' in bounds and 'q95' in bounds:

            for i in range(len(countries)):

                dfs = df[(df['Country/Region'] == countries[i])]

                data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['ci_65_u']), mode='lines',
                line=dict(color=col2[i], width=0.5), showlegend=False, hovertemplate='<b>'+countries[i]+
                ': %{y:.2f}</b><br>Upper Bound, 65% Credible Interval<br>%{x|%d %b %y}<extra></extra>'))

                data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['ci_65_l']), mode='lines',
                line=dict(color=col2[i], width=0.5), fill='tonexty', fillcolor=col2[i], showlegend=False,
                hovertemplate='<b>'+countries[i]+': %{y:.2f}</b><br>Lower Bound, 65% Credible Interval<br>'+
                '%{x|%d %b %y}<extra></extra>'))

                data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['ci_95_u']), mode='lines',
                line=dict(color=col3[i], width=0.5), showlegend=False, hovertemplate='<b>'+countries[i]+
                ': %{y:.2f}</b><br>Upper Bound, 95% Credible Interval<br>%{x|%d %b %y}<extra></extra>'))

                data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['ci_95_l']), mode='lines',
                line=dict(color=col3[i], width=0.5), fill='tonexty', fillcolor=col3[i], showlegend=False,
                hovertemplate='<b>'+countries[i]+': %{y:.2f}</b><br>Lower Bound, 95% Credible Interval<br>'+
                '%{x|%d %b %y}<extra></extra>'))

        elif 'q65' in bounds and 'q95' not in bounds:

            for i in range(len(countries)):

                dfs = df[(df['Country/Region'] == countries[i])]

                data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['ci_65_u']), mode='lines',
                line=dict(color=col2[i], width=0.5), showlegend=False, hovertemplate='<b>'+countries[i]+
                ': %{y:.2f}</b><br>Upper Bound, 65% Credible Interval<br>%{x|%d %b %y}<extra></extra>'))

                data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['ci_65_l']), mode='lines',
                line=dict(color=col2[i], width=0.5), fill='tonexty', fillcolor=col2[i], showlegend=False,
                hovertemplate='<b>'+countries[i]+': %{y:.2f}</b><br>Lower Bound, 65% Credible Interval<br>'+
                '%{x|%d %b %y}<extra></extra>'))

        elif 'q95' in bounds and 'q65' not in bounds:

            for i in range(len(countries)):

                dfs = df[(df['Country/Region'] == countries[i])]

                data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['ci_95_u']), mode='lines',
                line=dict(color=col3[i], width=0.5), showlegend=False, hovertemplate='<b>'+countries[i]+
                ': %{y:.2f}</b><br>Upper Bound, 95% Credible Interval<br>%{x|%d %b %y}<extra></extra>'))

                data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['ci_95_l']), mode='lines',
                line=dict(color=col3[i], width=0.5), fill='tonexty', fillcolor=col3[i], showlegend=False,
                hovertemplate='<b>'+countries[i]+': %{y:.2f}</b><br>Lower Bound, 95% Credible Interval<br>'+
                '%{x|%d %b %y}<extra></extra>'))

        for i in range(len(countries)):

            dfs = df[(df['Country/Region'] == countries[i])]

            data.append(go.Scatter(x=list(dfs['Date']), y=list(dfs['R']), mode='lines', name=countries[i],
            line=dict(color=col1[i], width=3), hovertemplate='<b>'+ countries[i]+': %{y:.2f}</b><br>%{x|%d %b %y}'+
            '<br><extra></extra>'))

        # create the chart object
        figure = go.Figure(data=data, layout=layout).to_dict()

        return figure

# callback for CSV file download
@app.callback([Output('download_link', 'href'), Output('download_link', 'download')],
              [Input('download_link', 'n_clicks')])
def download_file(clicks):

    # load the data
    df = pd.read_csv('database.csv')

    # convert the data to csv
    csv = df.to_csv(index=False, encoding='utf-8')

    # create the file for download
    file_for_download = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(csv)

    # use the current date/time as the file name
    file_name = 'database_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'

    return [file_for_download, file_name]

# callback for switching page
@app.callback(Output('page_content', 'children'), [Input('url', 'pathname')])
def switch_page(pathname):

    if pathname == '/FAQ':

        return faq_page

    else:

        return results_page

if __name__ == '__main__':
    application.run()




