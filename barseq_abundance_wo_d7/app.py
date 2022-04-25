#!/usr/bin/env python3
import flask
import math
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import time
from plotly.validators.scatter.marker import SymbolValidator
import math
import os.path
import dash_table

from dash.exceptions import PreventUpdate

import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np


##################################################################################################################
# loading files
##################################################################################################################

print("\n========= loading files =========\n")
################################################################################
filename1 = 'ALL_BL6_NP_VS_RAG1KO_NP_RGR_T_TEST_SUMMARY_PVAL_0.01.csv'
filename2 = 'ALL_BL6_P_VS_BL6_NP_RGR_T_TEST_SUMMARY_PVAL_0.01.csv'
filename3 = 'ALL_BL6_P_VS_RAG1KO_P_RGR_T_TEST_SUMMARY_PVAL_0.01.csv'
filename4 = 'ALL_RAG1KO_P_VS_RAG1KO_NP_RGR_T_TEST_SUMMARY_PVAL_0.01.csv'
################################################################################
DATA1 = pd.read_csv(filename1)
## List of unique genes
genes1 = DATA1['gene'].unique()
################################################################################
DATA2 = pd.read_csv(filename2)
## List of unique genes
genes2 = DATA2['gene'].unique()
################################################################################
DATA3 = pd.read_csv(filename3)
## List of unique genes
genes3 = DATA3['gene'].unique()
################################################################################
DATA4 = pd.read_csv(filename4)
## List of unique genes
genes4 = DATA4['gene'].unique()
################################################################################
common_list12 = [g for g in genes1 if g in genes2 ]
common_list34 = [g for g in genes3 if g in genes4 ]
common_list = [g for g in common_list12 if g in common_list34]
################################################################################
all_genes1 = [ {'label': key, 'value':key} for key in common_list ]
##### The main window layout
##################################################################################################################

print("\n========= starting server =========\n")

server = flask.Flask(__name__)
app = dash.Dash(
  __name__,
  server=server,
  routes_pathname_prefix='/barseq_abundances_wo_d7/')

pools = ['pool1', 'pool3', 'pool4', 'poolC1', 'poolC2','poolC5', "PBSTM139_PBSTM145", "PBSTM155_PBSTM158"]
# pools = ['pool1', 'pool3', 'pool4', 'poolC1', 'poolC2','poolC5', "PBSTM139_PBSTM145", "PBSTM155_PBSTM158"]
backgrounds = [ "NP_BL6", "P_BL6", "NP_RAG1KO", "P_RAG1KO"]
# backgrounds = [ "NP_BL6", "P_BL6", "NP_RAG1KO", "P_RAG1KO", "P_IFNyKO", "NP_IFNyKO"]

pool_options = [ {'label': key, 'value':key} for key in pools ]
background_options = [ {'label': key, 'value':key} for key in backgrounds ]

app.config.suppress_callback_exceptions = True ###Note, dangerous -- see if needed. used if components are added after initialization
app.layout = html.Div([
##################################################################################################################
#           NP BL6 Vs. NP RAG1KO
##################################################################################################################
            # gene selection through dropdown; this will add the gene id to the textbox above
            html.Div([
                    dcc.Dropdown(
                    id='genes-dropdown',
                    value = 'PBANKA_051500',
                    options=all_genes1,
                    placeholder='Select a gene using its name',)
            ], id='genes-dropdown-timestamp1', n_clicks_timestamp = 1,
            style = {'padding': '10px 5px'}),

            html.Div([
                    dcc.Dropdown(
                    id='background-dropdown',
                    value = 'P_BL6',
                    options=background_options,
                    placeholder='Select a background',)
            ], id='background-dropdown-timestamp1', n_clicks_timestamp = 1,
            style = {'padding': '10px 5px'}),

            html.Div([
                    dcc.Dropdown(
                    id='pool-dropdown',
                    value = 'PBSTM139_PBSTM145',
                    options=pool_options,
                    placeholder='Select a pool',)
            ], id='pool-dropdown-timestamp1', n_clicks_timestamp = 1,
            style = {'padding': '10px 5px'}),

            html.Div([dcc.Graph( id='scatter-plot')],
                style={   'display': 'inline-block', 'margin': '0 auto',
                'padding': '50px 50px'}),
##################################################################################################################
# ##################################################################################################################
                            ],
                style={
                  'position': 'inline-block',
                  'width': '95%',
                  'height': '95%',
                  'margin': '0 auto',
                  'padding':'0',
                  'overflow':'hidden'}
##################################################################################################################
                  )
##################################################################################################################
# Function: Make the scatter plot for all the genes
##################################################################################################################
@app.callback(Output('scatter-plot', 'figure'),
    [Input('genes-dropdown', 'value'),
    Input('background-dropdown', 'value'),
    Input('pool-dropdown', 'value')])
def scatterplot(selected_gene, selected_background, selected_pool):
#    print("ABUNDANCE_" + selected_background.upper() + "_" + selected_pool.upper() + ".csv")

    if os.path.isfile("ABUNDANCE_" + selected_background.upper() + "_" + selected_pool.upper() + ".csv"):
        DATA = pd.read_csv("ABUNDANCE_" + selected_background.upper() + "_" + selected_pool.upper() + ".csv")

        DATA1 = DATA[DATA["gene"] == selected_gene].copy()
#       mice2drop=[val for m,val in enumerate(DATA1["mice"].tolist()) if math.isnan(DATA1["abundance"].values[m])]
#       mice2drop = list(set(mice2drop))

#       DATA1 = DATA1[~DATA1["mice"].isin(mice2drop)]
    else:
        DATA1 = pd.DataFrame()


    if DATA1.empty:
        return {
                "layout": {
                    "xaxis": {
                        "visible": False
                        },
                    "yaxis": {
                        "visible": False
                        },
                    "annotations": [
                        {
                            "text": "No matching data found",
                            "xref": "paper",
                            "yref": "paper",
                            "showarrow": False,
                            "font": {
                                "size": 28
                                }
                            }
                        ]
                    }
                }
    else:

    #Create the basic plot
        fig1 = px.scatter(DATA1, x = 'day', y = 'abundance', color = 'mice', labels={ "day": "day", "abundance": "Barcode abundance(%)"})

        fig1.update_traces(mode='lines+markers')
        fig1.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
        return fig1
##################################################################################################################


##################################################################################################################
##### Callback: Update gene information box ... links
###########

# run the app on "python app.py";
# default port: 8050
if __name__ == '__main__':
    app.run_server(debug = True, port = 1427)

app = dash.Dash(__name__)
#viewer.show(app)
