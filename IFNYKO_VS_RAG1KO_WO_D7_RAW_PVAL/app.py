#!/usr/bin/env python3
import flask
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import time
from plotly.validators.scatter.marker import SymbolValidator
import math

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
# POOL C1
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
################################################################################
##### The main window layout
##################################################################################################################

print("\n========= starting server =========\n")

server = flask.Flask(__name__)
app = dash.Dash(
  __name__,
  server=server,
  routes_pathname_prefix='/WO_D7_RAW_PVAL/')

app.config.suppress_callback_exceptions = True ###Note, dangerous -- see if needed. used if components are added after initialization
app.layout = html.Div([
##################################################################################################################
#           NP BL6 Vs. NP RAG1KO
##################################################################################################################
            # gene selection through dropdown; this will add the gene id to the textbox above
            html.Div([
                    dcc.Dropdown(
                    id='genes-dropdown1',
                    value = '',
                    options=all_genes1,
                    placeholder='Select a gene using its name',)
            ], id='genes-dropdown-timestamp1', n_clicks_timestamp = 1,
            style = {'padding': '10px 5px'}),


 #           html.Label(" ".join(filename1.split(".")[0].split("_")[1:6])),
            html.Div([dcc.Graph( id='scatter-plot3')],
                style={   'display': 'inline-block', 'margin': '0 auto',
                'padding': '50px 50px'}),
##################################################################################################################
#           NP BL6 Vs. NP RAG1KO
##################################################################################################################
            html.Br(),

#            html.Label(" ".join(filename2.split(".")[0].split("_")[1:6])),
            html.Div([dcc.Graph( id='scatter-plot2')],
                style={   'display': 'inline-block', 'margin': '0 auto',
                'padding': '50px 50px'}),
# ##################################################################################################################
# ##################################################################################################################
            html.Br(),

#            html.Label(" ".join(filename3.split(".")[0].split("_")[1:6])),
            html.Div([dcc.Graph( id='scatter-plot1')],
                style={   'display': 'inline-block', 'margin': '0 auto',
                'padding': '50px 50px'}),
# ##################################################################################################################
            html.Br(),

#            html.Label(" ".join(filename4.split(".")[0].split("_")[1:6])),
            html.Div([dcc.Graph( id='scatter-plot4')],
                style={   'display': 'inline-block', 'margin': '0 auto',
                'padding': '50px 50px'}),
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
@app.callback(Output('scatter-plot1', 'figure'),
    [Input('genes-dropdown1', 'value')])
def scatterplot(selected_gene):

    DATA_PLOT1 = DATA1.copy()
    # import pdb; pdb.set_trace()
    gene_status1 = [ selected_gene if v == selected_gene else DATA1['significant_status'].values[i] for i, v in enumerate(genes1)]
    color_discrete_map = {'Not significant': 'rgb(255,0,0)', 'significant': 'rgb(0,255,0)', selected_gene: 'rgb(0,0,255)'}
    DATA_PLOT1['gene_status'] = gene_status1
    # DATA_PLOT1.sort_values(by='gene_status', inplace = True)

    #Create the basic plot
    fig1 = px.scatter(DATA_PLOT1[DATA_PLOT1.gene_status.isin(['Not significant','significant',selected_gene])], x = 'rgr_bl6_np', y = 'rgr_rag1ko_np', color_discrete_map = color_discrete_map,
        hover_data = ['gene','pvalue','pvalue_corrected','pheno_bl6_np','pheno_rag1ko_np','rgr_bl6_np','rgr_bl6_np','gene_product','significant_status'], color = 'gene_status', labels={ "rgr_bl6_np": "Relative.Growth.Rate (BL6 NP)", "rgr_rag1ko_np": "Relative.Growth.Rate (RAG1KO NP)"})

    fig1.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
    return fig1
##################################################################################################################
##################################################################################################################
@app.callback(Output('scatter-plot2', 'figure'),
    [Input('genes-dropdown1', 'value')])
def scatterplot(selected_gene):

    DATA_PLOT2 = DATA2.copy()
    # import pdb; pdb.set_trace()
    gene_status2 = [ selected_gene if v == selected_gene else DATA2['significant_status'].values[i] for i, v in enumerate(genes2)]
    color_discrete_map = {'Not significant': 'rgb(255,0,0)', 'significant': 'rgb(0,255,0)', selected_gene: 'rgb(0,0,255)'}
    DATA_PLOT2['gene_status'] = gene_status2

    #Create the basic plot
    fig2 = px.scatter(DATA_PLOT2[DATA_PLOT2.gene_status.isin(['Not significant','significant',selected_gene])], x = 'rgr_bl6_np', y = 'rgr_bl6_p', color_discrete_map = color_discrete_map,
        hover_data = ['gene','pvalue','pvalue_corrected','pheno_bl6_np','pheno_bl6_p','rgr_bl6_np','rgr_bl6_p','gene_product','significant_status'], color = 'gene_status', labels={ "rgr_bl6_np": "Relative.Growth.Rate (BL6 NP)", "rgr_bl6_p": "Relative.Growth.Rate (BL6 P)"})

    fig2.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
    return fig2
# ##################################################################################################################
##################################################################################################################
@app.callback(Output('scatter-plot3', 'figure'),
    [Input('genes-dropdown1', 'value')])
def scatterplot(selected_gene):

    DATA_PLOT3 = DATA3.copy()
    # import pdb; pdb.set_trace()
    gene_status3 = [ selected_gene if v == selected_gene else DATA3['significant_status'].values[i] for i, v in enumerate(genes3)]
    color_discrete_map = {'Not significant': 'rgb(255,0,0)', 'significant': 'rgb(0,255,0)', selected_gene: 'rgb(0,0,255)'}
    DATA_PLOT3['gene_status'] = gene_status3

    #Create the basic plot
    fig3 = px.scatter(DATA_PLOT3[DATA_PLOT3.gene_status.isin(['Not significant','significant',selected_gene])], x = 'rgr_bl6_p', y = 'rgr_rag1ko_p', color_discrete_map = color_discrete_map,
        hover_data = ['gene','pvalue','pvalue_corrected','pheno_bl6_p','pheno_rag1ko_p','rgr_bl6_p','rgr_rag1ko_p','gene_product','significant_status'], color = 'gene_status', labels={ "rgr_bl6_p": "Relative.Growth.Rate (BL6 P)", "rgr_rag1ko_p": "Relative.Growth.Rate (RAG1KO P)"})

    fig3.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
    return fig3

##################################################################################################################
##################################################################################################################
@app.callback(Output('scatter-plot4', 'figure'),
    [Input('genes-dropdown1', 'value')])
def scatterplot(selected_gene):

    DATA_PLOT4 = DATA4.copy()
    # import pdb; pdb.set_trace()
    gene_status4 = [ selected_gene if v == selected_gene else DATA4['significant_status'].values[i] for i, v in enumerate(genes4)]
    color_discrete_map = {'Not significant': 'rgb(255,0,0)', 'significant': 'rgb(0,255,0)', selected_gene: 'rgb(0,0,255)'}
    DATA_PLOT4['gene_status'] = gene_status4

    #Create the basic plot
    fig4 = px.scatter(DATA_PLOT4[DATA_PLOT4.gene_status.isin(['Not significant','significant',selected_gene])], x = 'rgr_RAG1KO_p', y = 'rgr_RAG1KO_np', color_discrete_map = color_discrete_map,
        hover_data = ['gene','pvalue','pvalue_corrected','pheno_RAG1KO_p','pheno_RAG1KO_np','rgr_RAG1KO_p','rgr_RAG1KO_np','gene_product','significant_status'], color = 'gene_status', labels={ "rgr_RAG1KO_p": "Relative.Growth.Rate (RAG1KO P)", "rgr_RAG1KO_np": "Relative.Growth.Rate (RAG1KO NP)"})

    fig4.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
    return fig4

##################################################################################################################
##### Callback: Update gene information box ... links
###########

# run the app on "python app.py";
# default port: 8050
if __name__ == '__main__':
    app.run_server(debug = True, port = 1916)

app = dash.Dash(__name__)
#viewer.show(app)
