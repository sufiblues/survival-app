import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from lifelines import KaplanMeierFitter
from lifelines import CoxPHFitter

import plotly.express as px
import plotly.graph_objs as go



import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='content_name'),
    dcc.Store(id="survival_data",storage_type = 'local'),
    dcc.Dropdown(
        id='fitting_function',
        options=[
            {'label': 'Cox Regression', 'value': 'CPH'},
            {'label': 'Kaplan Meier Curve', 'value': 'KM'},
            {'label': 'Weibull Curve', 'value': 'WB'}
        ],
        value='KM'
    ),
    #fill in later in callback
    dcc.Dropdown(
        id='parts_dropdown',
        placeholder="Enter in part"
    ),
    html.Div(id="fitted_functions"),
])


def parse_contents(contents, filename):
    if not contents:
        return None
    content_type, content_string = contents.split(',')
    df = pd.DataFrame()
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df.to_json()

@app.callback(Output("fitted_functions","children"),
              Input("survival_data","data"),
              Input("parts_dropdown","value"))
def plot_kmf(data,part):
    if not data:
        return html.Div("Empty")
    else:
        df = pd.read_json(data)
        kmf = kmftest(df,part)
        fig = create_figure_from_kmf(kmf)
        return dcc.Graph(figure = fig)

@app.callback(Output('content_name', 'children'),
              Output("survival_data",'data'),
              Output("parts_dropdown", "options"),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(contents, filename):
    data = parse_contents(contents,filename)
    df = pd.DataFrame
    if data:        
        df = pd.read_json(data)
    if data:
        #TODO: set value to top of parts list
        return html.Div(filename), data, [{'label': i, 'value':i} for i in df['sex'].unique()]
    else:
        return html.Div(filename), data, [] 
    




def kmftest(df,part):
    kmf = KaplanMeierFitter()
    #filter dataset on part
    df = df[df["sex"] == part]
    #dataframe = dataframe[dataframe['part'] == part]
    #TODO: change to duration later
    T = df['time']
    #TODO: chagne this key to the right dataset.
    E = df['status']
    kmf.fit(df['time'], event_observed = df['status'])
    return kmf

def create_figure_from_kmf(kmf):
    X = kmf.survival_function_.reset_index()['timeline']
    Y = kmf.survival_function_['KM_estimate']
    c_lower = kmf.confidence_interval_["KM_estimate_lower_0.95"]
    c_upper = kmf.confidence_interval_["KM_estimate_upper_0.95"]
    fig = go.Figure([
        go.Scatter(
            name='Estimate',
            x=X,
            y=Y,
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
        ),
        go.Scatter(
            name='Upper Bound',
            x=X,
            y=c_upper,
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=X,
            y=c_lower,
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
