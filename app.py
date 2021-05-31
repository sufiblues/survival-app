import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import plotly.express as px


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
    html.Div(id="isdatahere"),
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

@app.callback(Output("isdatahere","children"),
              Input("survival_data","data"))
def test(data):
    if not data:
        return html.Div("Empty")
    else:
        df = pd.read_json(data)
        fig = px.scatter(df, x="status", y = "time")
        return dcc.Graph(figure = fig)


@app.callback(Output('content_name', 'children'),
              Output("survival_data",'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(contents, filename):
    data = parse_contents(contents,filename)
    return html.Div(filename), data
    



if __name__ == '__main__':
    app.run_server(debug=True)
