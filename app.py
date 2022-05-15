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
from dash.dash import no_update
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly import tools

import pandas as pd
import numpy as np

def getList(dict):
    list = []
    for key in dict.keys():
        list.append(key)
    return list


print("\n========= starting server =========\n")

server = flask.Flask(__name__)
app = dash.Dash(
  __name__,
  server=server,
  routes_pathname_prefix='/barseqviewer2/')

##################################################################################################################
gene_dropdown_data = pd.read_csv("gene_dropdown.csv")
gene_dropdown_list = gene_dropdown_data['gene'].tolist()
gene_options = [{'label': key, 'value':key} for key in gene_dropdown_list]

##################################################################################################################
data_sets = ["BL6 Vs. Rag1KO", "BL6 Vs. IFNyKO", "Single Transfection", "BL6 Vs. Rag1KO minipool2"]
data_set_options = [ {'label': key, 'value':key} for key in data_sets ]

##################################################################################################################
rag1ko_pools = ['pool1', 'pool3', 'pool4', 'poolC1', 'poolC2', "PBSTM139_PBSTM145", "PBSTM155_PBSTM158"]
rag1ko_backgrounds = [ "NP_BL6", "P_BL6", "NP_RAG1KO", "P_RAG1KO"]

rag1ko_pool_options = [ {'label': key, 'value':key} for key in rag1ko_pools ]
rag1ko_background_options = [ {'label': key, 'value':key} for key in rag1ko_backgrounds ]
##################################################################################################################

ifnyko_pools = ['poolC3', 'poolC4']
ifnyko_backgrounds = [ "NP_BL6", "P_BL6", "NP_IFNYKO", "P_IFNYKO"]

ifnyko_pool_options = [ {'label': key, 'value':key} for key in ifnyko_pools ]
ifnyko_background_options = [ {'label': key, 'value':key} for key in ifnyko_backgrounds ]
##################################################################################################################
minipool2_pools = ['minipool2']
minipool2_backgrounds = [ "P_BL6", "P_RAG1KO"]

minipool2_pool_options = [ {'label': key, 'value':key} for key in minipool2_pools ]
minipool2_background_options = [ {'label': key, 'value':key} for key in minipool2_backgrounds ]
##################################################################################################################

st_pools = ['poolC5']
st_backgrounds = [ "NP_BL6", "P_BL6", "NP_RAG1KO", "P_RAG1KO"]

st_pool_options = [ {'label': key, 'value':key} for key in st_pools ]
st_background_options = [ {'label': key, 'value':key} for key in st_backgrounds ]

##################################################################################################################
time_series = ["ALLDAYS", "WO_D7"]
time_series_options = [ {'label': key, 'value':key} for key in time_series ]

##################################################################################################################
#pvals = ["RAW", "ADJ"]
#pval_options = [ {'label': key, 'value':key} for key in pvals ]

##################################################################################################################
plottypes = ["scatter", "time series"]
plot_type_options = [ {'label': key, 'value':key} for key in plottypes ]

##################################################################################################################
experiment_dict = {
       "BL6 Vs. Rag1KO scatter ALLDAYS RAW": "ALLDAYS_RAW_PVAL",
       "BL6 Vs. Rag1KO scatter ALLDAYS ADJ": "ALLDAYS_ADJ_PVAL",

       "BL6 Vs. Rag1KO scatter WO_D7 RAW": "WO_D7_RAW_PVAL",
       "BL6 Vs. Rag1KO scatter WO_D7 ADJ": "WO_D7_ADJ_PVAL",

       "BL6 Vs. Rag1KO time series ALLDAYS": "barseq_abundance",
       "BL6 Vs. Rag1KO time series WO_D7": "barseq_abundance_wo_d7",

       "BL6 Vs. IFNyKO scatter ALLDAYS RAW": "INTERFERON_ALLDAYS_RAW_PVAL",
       "BL6 Vs. IFNyKO scatter ALLDAYS ADJ": "INTERFERON_ALLDAYS_ADJ_PVAL",

       "BL6 Vs. IFNyKO scatter WO_D7 RAW": "INTERFERON_WO_D7_RAW_PVAL",
       "BL6 Vs. IFNyKO scatter WO_D7 ADJ": "INTERFERON_WO_D7_ADJ_PVAL",

       "BL6 Vs. IFNyKO time series ALLDAYS": "interferon_barseq_abundances",
       "BL6 Vs. IFNyKO time series WO_D7": "interferon_barseq_abundances_wo_d7",

       "Single Transfection scatter ALLDAYS RAW": "POOLC5_RAW_PVAL",
       "Single Transfection scatter ALLDAYS ADJ": "POOLC5_ADJ_PVAL",

       "Single Transfection scatter WO_D7 RAW": "POOLC5_WO_D7_RAW_PVAL",
       "Single Transfection scatter WO_D7 ADJ": "POOLC5_WO_D7_ADJ_PVAL",

       "Single Transfection time series ALLDAYS": "single_transfection_barseq_abundances",
       "Single Transfection time series WO_D7": "single_transfection_barseq_abundances_wo_d7",

       "BL6 Vs. Rag1KO minipool2 scatter ALLDAYS RAW": "MINIPOOL2_ALLDAYS_RAW_PVAL",
       "BL6 Vs. Rag1KO minipool2 scatter ALLDAYS ADJ": "MINIPOOL2_ALLDAYS_ADJ_PVAL",

       "BL6 Vs. Rag1KO minipool2 scatter WO_D7 RAW": "MINIPOOL2_WO_D7_RAW_PVAL",
       "BL6 Vs. Rag1KO minipool2 scatter WO_D7 ADJ": "MINIPOOL2_WO_D7_ADJ_PVAL",

       "BL6 Vs. Rag1KO minipool2 time series ALLDAYS": "barseq_abundance",
       "BL6 Vs. Rag1KO minipool2 time series WO_D7": "barseq_abundance_wo_d7"
       }
dict_list = getList(experiment_dict)




################################################################################
##### The main window layout
################################################################################
app.config.suppress_callback_exceptions = True ###Note, dangerous -- see if needed. used if components are added after initialization
app.layout = html.Div([
    html.Div([
                html.Div([
                    html.Label("Experimental series:"),
                    dcc.Dropdown(
                        id='experiment-dropdown',
                        value = 'BL6 Vs. Rag1KO',
                        options = data_set_options,
                        placeholder='Select an experiment',
                        style={'width': '100%'}),
                ], style = {'padding': '10px 10px', 'display': 'inline-block', 'text-align': 'justify', 'width': '15%'}),

                html.Div([
	            html.Label("Plot type:"),
                    dcc.Dropdown(
                        id='plottype-dropdown',
                        value = 'scatter',
                        options = plot_type_options,
                        placeholder='Select plot type',
                        style={'width': '100%'}),
                ], style = {'padding': '10px 10px', 'display': 'inline-block', 'text-align': 'justify', 'width': '15%'}),

                html.Div([
                    html.Label("Days:"),
                    dcc.Dropdown(
                        id='timeseries-dropdown',
                        value = 'ALLDAYS',
                        options = time_series_options,
                        placeholder='Select time series type',
                        style={'width': '100%'}),
                ], style = {'padding': '10px 10px', 'display': 'inline-block', 'text-align': 'justify', 'width': '15%'}),

                html.Div([
                    html.Label("Gene:"),
                    dcc.Dropdown(
                        id='gene-dropdown',
                        value = 'PBANKA_010110',
                        options = gene_options,
                        placeholder = 'Select gene',
                        style = {'width': '100%'}),
                ], style = {'padding': '10px 10px', 'display': 'inline-block', 'text-align': 'justify', 'width': '15%'}),


    ], style = {'padding': '0px 0px', 'display': 'inline-block', 'text-align': 'justify', 'width': '100%'}),
    html.Div([

                html.Div([
                    html.A([
                        html.Img(src=app.get_asset_url('MIMS_logo_blue.svg'), style={
                               'height': '30px',
                               'padding': '10px 10px'}),
                        ], href='http://www.mims.umu.se/')
                ], style = {'padding': '10px 10px', 'display': 'inline-block', 'text-align': 'justify', 'width': '15%'}),

                html.Div([
                    html.Label(id="opt1-label"),
                    dcc.Dropdown(id='opt1-dropdown', style={'width': '100%'}),
                ], style = {'padding': '10px 10px', 'display': 'inline-block', 'text-align': 'justify', 'width': '15%'}),

                html.Div([
                    html.Label(id="opt2-label"),
                    dcc.Dropdown(id='opt2-dropdown', style = {'width': '100%'}),
                ], style = {'padding': '10px 10px', 'display': 'inline-block', 'text-align': 'justify', 'width': '15%'})

    ], style = {'padding': '0px 0px', 'display': 'inline-block', 'text-align': 'justify', 'width': '100%'}),
    ########################### 4 plot panels ###########################
    html.Div(
        className="row", children=[
            html.Div([dcc.Graph( id='plot1')], style={   'display': 'inline-block', 'margin': '0 auto', 'padding': '50px 50px', 'width': '50%'}),
            html.Div([dcc.Graph( id='plot2')], style={   'display': 'inline-block', 'margin': '0 auto', 'padding': '50px 50px', 'width': '50%'}),
        ], style={
                  'position': 'inline-block',
                  'width': '100%',
                  'height': '50%',
                  'margin': '0 auto',
                  'padding':'0'
        }
    ),
    html.Div(
        className="row", children=[
            html.Div([dcc.Graph( id='plot3')], style={   'display': 'inline-block', 'margin': '0 auto', 'padding': '50px 50px', 'width': '50%'}),
            html.Div([dcc.Graph( id='plot4')], style={   'display': 'inline-block', 'margin': '0 auto', 'padding': '50px 50px', 'width': '50%'})
        ], style={
                  'position': 'inline-block',
                  'width': '100%',
                  'height': '50%',
                  'margin': '0 auto',
                  'padding':'0'
        }
    )



])


###################################################################################################################
# Decide when to show opt1
@app.callback(
    [dash.dependencies.Output('opt1-dropdown', 'style'),
     dash.dependencies.Output('opt1-label', 'children')],
    [dash.dependencies.Input('plottype-dropdown', 'value')])
def toggle_container2(toggle_value):

    if toggle_value == 'time series':
        return {'display': 'block'},"Pool:"
    else:
        return {'display': 'none'},""


##################################################################################################################
@app.callback(
    [dash.dependencies.Output('opt2-dropdown', 'style'),
     dash.dependencies.Output('opt2-label', 'children')],
    [dash.dependencies.Input('plottype-dropdown', 'value')])
def toggle_container2(toggle_value):

    if toggle_value == 'time series':
        return {'display': 'block'},"Treatment / Genotype:"
    else:
        return {'display': 'none'},""

##################################################################################################################
@app.callback(
    dash.dependencies.Output('plot2', 'style'),
    [dash.dependencies.Input('plottype-dropdown', 'value')])
def toggle_container2(toggle_value):

    if toggle_value == 'scatter':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

##################################################################################################################
@app.callback(
    dash.dependencies.Output('plot3', 'style'),
    [dash.dependencies.Input('plottype-dropdown', 'value')])
def toggle_container2(toggle_value):
    if toggle_value == 'scatter':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

##################################################################################################################
@app.callback(
    dash.dependencies.Output('plot4', 'style'),
    [dash.dependencies.Input('plottype-dropdown', 'value')])
def toggle_container2(toggle_value):

    if toggle_value == 'scatter':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

###################################################################################################################
@app.callback(
    [dash.dependencies.Output('opt1-dropdown', 'options'),
    dash.dependencies.Output('opt1-dropdown', 'placeholder')],
    [dash.dependencies.Input('experiment-dropdown', 'value'),
    dash.dependencies.Input('plottype-dropdown', 'value'),
    dash.dependencies.Input('timeseries-dropdown', 'value')]
)
def update_dropdown1(experiment,plot,time):

    if experiment == "BL6 Vs. Rag1KO" and plot == "time series":
        return rag1ko_pool_options, 'Select pool'
    elif experiment == "BL6 Vs. IFNyKO" and plot == "time series":
        return ifnyko_pool_options, 'Select pool'
    elif experiment == "Single Transfection" and plot == "time series":
        return st_pool_options, 'Select pool'
    elif experiment == "BL6 Vs. Rag1KO minipool2" and plot == "time series":
        return minipool2_pool_options, 'Select pool'
    else:
#        return pval_options, 'Select p-value'
        return [], 'Select p-value'

##################################################################################################################
@app.callback(
    [dash.dependencies.Output('opt2-dropdown', 'options'),
    dash.dependencies.Output('opt2-dropdown', 'placeholder')],
    [dash.dependencies.Input('experiment-dropdown', 'value'),
    dash.dependencies.Input('plottype-dropdown', 'value'),
    dash.dependencies.Input('timeseries-dropdown', 'value')]
)
def update_dropdown2(experiment,plot,time):

    if experiment == "BL6 Vs. Rag1KO" and plot == "time series":
        return rag1ko_background_options, 'Select background'
    elif experiment == "BL6 Vs. IFNyKO" and plot == "time series":
        return ifnyko_background_options, 'Select background'
    elif experiment == "BL6 Vs. Rag1KO minipool2" and plot == "time series":
        return minipool2_background_options, 'Select background'
    else:
        return st_background_options, 'Select background'


##################################################################################################################
#the scatter plot for all the genes
@app.callback(Output('plot1', 'figure'),
    [Input('experiment-dropdown', 'value'),
    Input('plottype-dropdown', 'value'),
    Input('timeseries-dropdown', 'value'),
    Input('opt1-dropdown', 'value'),
    Input('opt2-dropdown', 'value'),
    Input('gene-dropdown', 'value')])
def update_plot(selected_experiment, selected_plottype, selected_timeseries, selected_opt1, selected_opt2, selected_gene):

    print(selected_experiment, selected_plottype, selected_timeseries, selected_opt1)

    key1 = " "
    key2 = " "

    if selected_experiment and selected_plottype and selected_timeseries and selected_gene:
        #key1 = selected_experiment + " " + selected_plottype + " " + selected_timeseries + " " + selected_opt1
        key1 = selected_experiment + " " + selected_plottype + " " + selected_timeseries + " ADJ"

    if selected_experiment and selected_plottype and selected_timeseries and selected_gene and selected_opt1:
        #key1 = selected_experiment + " " + selected_plottype + " " + selected_timeseries + " " + selected_opt1
        key2 = selected_experiment + " " + selected_plottype + " " + selected_timeseries


    if selected_plottype == "scatter" and key1 in experiment_dict.keys():
        ##################################################################################################################
        # All the scatter plots
        ##################################################################################################################
        DATA_DIR = experiment_dict[key1]
        if selected_experiment == "BL6 Vs. Rag1KO minipool2":
            mutant = "RAG1KO"
            ################################################################################
            filename = DATA_DIR + "/ALL_BL6_P_VS_" + mutant + "_P_RGR_T_TEST_SUMMARY_PVAL_0.01.csv"
            DATA = pd.read_csv(filename)
            ################################################################################
            DATA_PLOT = DATA.copy()
            gene_status = [ selected_gene if v == selected_gene else DATA_PLOT['significant_status'].values[i] for i, v in enumerate(DATA_PLOT["gene"].tolist())]

            color_discrete_map = {'Not significant': 'rgb(255,0,0)', 'significant': 'rgb(0,255,0)', selected_gene: 'rgb(0,0,255)'}
            DATA_PLOT['gene_status'] = gene_status

            #Create the basic plot
            fig = px.scatter(DATA_PLOT[DATA_PLOT.gene_status.isin(['Not significant','significant',selected_gene])], x = 'rgr_bl6_p', y = 'rgr_' + mutant.lower() + '_p', color_discrete_map = color_discrete_map,
                hover_data = ['gene','pvalue','pvalue_corrected','pheno_bl6_p','pheno_' + mutant.lower() + '_p','rgr_bl6_p','rgr_bl6_p','gene_product','significant_status'], color = 'gene_status', labels={ "rgr_bl6_p": "Relative.Growth.Rate (BL6 P)", "rgr_" + mutant.lower() + "_p": "Relative.Growth.Rate (" + mutant + " P)"})

            #fig.update_layout() # autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
            #fig.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
            fig.update_layout( width = "50%", height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})

            return fig
        else:
            ################################################################################
            if selected_experiment == "BL6 Vs. Rag1KO":
                mutant = "RAG1KO"
            if selected_experiment == "BL6 Vs. IFNyKO":
                mutant = "IFNYKO"
            if selected_experiment == "Single Transfection":
                mutant = "RAG1KO"

            ################################################################################
            filename1 = DATA_DIR + "/ALL_BL6_NP_VS_" + mutant + "_NP_RGR_T_TEST_SUMMARY_PVAL_0.01.csv"
            filename2 = DATA_DIR + "/ALL_BL6_P_VS_BL6_NP_RGR_T_TEST_SUMMARY_PVAL_0.01.csv"
            filename3 = DATA_DIR + "/ALL_BL6_P_VS_" + mutant + "_P_RGR_T_TEST_SUMMARY_PVAL_0.01.csv"
            filename4 = DATA_DIR + "/ALL_" + mutant + "_P_VS_" + mutant + "_NP_RGR_T_TEST_SUMMARY_PVAL_0.01.csv"

            ################################################################################
            ## List of unique genes
            DATA1 = pd.read_csv(filename1)
            DATA2 = pd.read_csv(filename2)
            DATA3 = pd.read_csv(filename3)
            DATA4 = pd.read_csv(filename4)

            ################################################################################
            genes1 = DATA1['gene'].unique()
            genes2 = DATA2['gene'].unique()
            genes3 = DATA3['gene'].unique()
            genes4 = DATA4['gene'].unique()
            common_list12 = [g for g in genes1 if g in genes2 ]
            common_list34 = [g for g in genes3 if g in genes4 ]
            common_list = [g for g in common_list12 if g in common_list34]
            common_list.sort()

            ################################################################################
            ## List of unique genes in common to all the datasets... why do we need to do this?
            #common_list = list(intersection(set(DATA1['gene']), set(DATA2['gene']), set(DATA3['gene']), set(DATA4['gene'])))
            #common_list.sort()


            ################################################################################
            DATA1 = DATA1[DATA1["gene"].isin(common_list)]
            DATA2 = DATA2[DATA2["gene"].isin(common_list)]
            DATA3 = DATA3[DATA3["gene"].isin(common_list)]
            DATA4 = DATA4[DATA4["gene"].isin(common_list)]

            figtot = make_subplots(
                rows=2, cols=2,
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "scatter"}]])

            def makeplot(DATA1, usex, usey):
                DATA_PLOT1 = DATA1.copy()
                gene_status1 = [ selected_gene if v == selected_gene else DATA_PLOT1['significant_status'].values[i] for i, v in enumerate(DATA_PLOT1["gene"].tolist())]
                color_discrete_map = {'Not significant': 'rgb(255,0,0)', 'significant': 'rgb(0,255,0)', selected_gene: 'rgb(0,0,255)'}
                DATA_PLOT1['gene_status'] = gene_status1

                hover_data = ["<br>".join([str(i)+":"+str(rec[i]) for d,i in enumerate(rec)]) 
                                       for rec in DATA_PLOT1.to_dict('records')]

                usedat = DATA_PLOT1[DATA_PLOT1.gene_status.isin(['Not significant','significant',selected_gene])]
                fig1 = go.Scatter(
                    mode = 'markers',
                    x = usedat[usex],
                    y = usedat[usey],
                    marker_color = [color_discrete_map[c] for c in usedat['gene_status']],
                    hovertext = hover_data
                )
                return fig1

            fig1 = makeplot(DATA1, 'rgr_bl6_np',             'rgr_' + mutant.lower() + '_np')
            fig2 = makeplot(DATA2, 'rgr_bl6_np',             'rgr_bl6_p')
            fig3 = makeplot(DATA3, 'rgr_bl6_p',              'rgr_' + mutant.lower() + '_p')
            fig4 = makeplot(DATA4, 'rgr_' + mutant + '_p',   'rgr_' + mutant + '_np')

            figtot.add_trace(fig1,row=1, col=1)
            figtot.update_xaxes(title_text="Relative.Growth.Rate (BL6 NP)", row=1, col=1)
            figtot.update_yaxes(title_text="Relative.Growth.Rate (" + mutant + " NP)", row=1, col=1)

            figtot.add_trace(fig2,row=1, col=2)
            figtot.update_xaxes(title_text="Relative.Growth.Rate (BL6 NP)", row=1, col=2)
            figtot.update_xaxes(title_text="Relative.Growth.Rate (BL6 P)", row=1, col=2)

            figtot.add_trace(fig3,row=2, col=1)
            figtot.update_xaxes(title_text="Relative.Growth.Rate (BL6 P)", row=2, col=1)
            figtot.update_yaxes(title_text="Relative.Growth.Rate (" + mutant + " P)", row=2, col=1)

            figtot.add_trace(fig4,row=2, col=2)
            figtot.update_xaxes(title_text="Relative.Growth.Rate (" + mutant + " P)", row=2, col=2)
            figtot.update_yaxes(title_text="Relative.Growth.Rate (" + mutant + " NP)", row=2, col=2)

            figtot.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
            return figtot


    elif selected_plottype == "time series" and key2 in experiment_dict.keys() and selected_opt2:
        ##################################################################################################################
        # Time series plots
        ##################################################################################################################
        DATA_DIR = experiment_dict[key2]
        plotdatafile = DATA_DIR + "/ABUNDANCE_" + selected_opt2.upper() + "_" + selected_opt1.upper() + ".csv"

        if os.path.isfile(plotdatafile):
            DATA = pd.read_csv(plotdatafile)
            DATA1 = DATA[DATA["gene"] == selected_gene].copy()

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
            fig1 = px.scatter(DATA1, x = 'day', y = 'abundance', color = 'mice', labels={ "day": "day", "abundance": "Barcode abundance(%)"})
            fig1.update_traces(mode='lines+markers')
            fig1.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
            return fig1
    else:
        ##################################################################################################################
        # All plots disabled
        ##################################################################################################################
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
                            "text": "Incomplete selection",
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




##################################################################################################################
##### Callback: Update gene information box ... links
###########

# run the app on "python app.py";
# default port: 8050
if __name__ == '__main__':
    app.run_server(host='127.0.0.1',debug = True, port = 15590)

app = dash.Dash(__name__)
#viewer.show(app)
