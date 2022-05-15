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
from os import listdir
from os.path import isfile, join
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
def experiment_to_mutant(selected_experiment):
    mutant = "nomut"
    if selected_experiment == "BL6 Vs. Rag1KO minipool2":
        mutant = "RAG1KO"
    if selected_experiment == "BL6 Vs. Rag1KO":
        mutant = "RAG1KO"
    if selected_experiment == "BL6 Vs. IFNyKO":
        mutant = "IFNYKO"
    if selected_experiment == "Single Transfection":
        mutant = "RAG1KO"
    return mutant

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

ifnyko_pools = ['poolC3', 'poolC4']
ifnyko_backgrounds = [ "NP_BL6", "P_BL6", "NP_IFNYKO", "P_IFNYKO"]

ifnyko_pool_options = [ {'label': key, 'value':key} for key in ifnyko_pools ]
ifnyko_background_options = [ {'label': key, 'value':key} for key in ifnyko_backgrounds ]

minipool2_pools = ['minipool2']
minipool2_backgrounds = [ "P_BL6", "P_RAG1KO"]

minipool2_pool_options = [ {'label': key, 'value':key} for key in minipool2_pools ]
minipool2_background_options = [ {'label': key, 'value':key} for key in minipool2_backgrounds ]

st_pools = ['poolC5']
st_backgrounds = [ "NP_BL6", "P_BL6", "NP_RAG1KO", "P_RAG1KO"]

st_pool_options = [ {'label': key, 'value':key} for key in st_pools ]
st_background_options = [ {'label': key, 'value':key} for key in st_backgrounds ]

def experiment_to_backgrounds(experiment):
    if experiment == "BL6 Vs. Rag1KO":
        return rag1ko_background_options
    elif experiment == "BL6 Vs. IFNyKO":
        return ifnyko_background_options
    elif experiment == "BL6 Vs. Rag1KO minipool2":
        return minipool2_background_options
    else:
        return st_background_options





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


experiment_meta = pd.read_csv("metadata.txt")
experiment_dict = dict(zip(experiment_meta["name"].tolist(),experiment_meta["file"].tolist()))
#print(experiment_dict)


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


                html.Div([
                    html.A([
                        html.Img(src=app.get_asset_url('MIMS_logo_blue.svg'), style={
                               'height': '30px',
                               'padding': '10px 10px'}),
                        ], href='http://www.mims.umu.se/')
                ], style = {'padding': '10px 10px', 'display': 'inline-block', 'text-align': 'justify', 'width': '15%'}),

    ], style = {'padding': '0px 0px', 'display': 'inline-block', 'text-align': 'justify', 'width': '100%'}),

    ########################### plot panel, scatter ###########################
    html.Div(
        className="row", children=[
            html.Div([dcc.Graph( id='plot1')], style={   'display': 'inline-block', 'margin': '0 auto', 'padding': '50px 50px', 'width': '100%'})
        ], style={
                  'position': 'inline-block',
                  'width': '100%',
                  'height': '50%',
                  'margin': '0 auto',
                  'padding':'0'
        }
    ),
    ########################### plot panel, time series ###########################
    html.Div(
        className="row", children=[
            html.Div([dcc.Graph( id='plot2')], style={   'display': 'inline-block', 'margin': '0 auto', 'padding': '50px 50px', 'width': '100%'})
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
        return {'display': 'none'},""


##################################################################################################################
@app.callback(
    [dash.dependencies.Output('opt2-dropdown', 'style'),
     dash.dependencies.Output('opt2-label', 'children')],
    [dash.dependencies.Input('plottype-dropdown', 'value')])
def toggle_container2(toggle_value):
        return {'display': 'none'},""




##################################################################################################################
#the scatter plot for all the genes
@app.callback(Output('plot1', 'figure'),
    [Input('experiment-dropdown', 'value'),
    Input('timeseries-dropdown', 'value'),
    Input('gene-dropdown', 'value')])
def update_plot_scatter(selected_experiment, selected_timeseries, selected_gene):

    key1 = " "
    if selected_experiment and selected_timeseries and selected_gene:
        key1 = selected_experiment + " scatter " + selected_timeseries + " ADJ"

    if key1 in experiment_dict.keys():
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
            # which mutant to compare to?
            mutant = experiment_to_mutant(selected_experiment)

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
                    hovertext = hover_data, showlegend=False
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
            figtot.update_yaxes(title_text="Relative.Growth.Rate (BL6 P)", row=1, col=2)

            figtot.add_trace(fig3,row=2, col=1)
            figtot.update_xaxes(title_text="Relative.Growth.Rate (BL6 P)", row=2, col=1)
            figtot.update_yaxes(title_text="Relative.Growth.Rate (" + mutant + " P)", row=2, col=1)

            figtot.add_trace(fig4,row=2, col=2)
            figtot.update_xaxes(title_text="Relative.Growth.Rate (" + mutant + " P)", row=2, col=2)
            figtot.update_yaxes(title_text="Relative.Growth.Rate (" + mutant + " NP)", row=2, col=2)

            figtot.update_layout( autosize= False, width = 1200, height = 600, margin={'t':0, 'b':0,'l':0, 'r':0})
            return figtot

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
# Time series plots
##################################################################################################################
@app.callback(Output('plot2', 'figure'),
    [Input('experiment-dropdown', 'value'),
    Input('timeseries-dropdown', 'value'),
    Input('gene-dropdown', 'value')])
def update_plot_ts(selected_experiment, selected_timeseries, selected_gene):

    mutant = experiment_to_mutant(selected_experiment)
    genotypes_to_compare = ["P_BL6","NP_BL6","P_"+mutant,"NP_"+mutant]

    allpools=[]
    for onegeno in genotypes_to_compare:
        onlyfiles = [f for f in listdir("barseq_abundance") if os.path.exists(join("barseq_abundance", f)) and isfile(join("barseq_abundance", f))]
        onlyfiles = [f for f in onlyfiles if f.startswith("ABUNDANCE_"+onegeno+"_")]
        allpools.extend([{"file":f,"name":onegeno + " / "+f[len("ABUNDANCE_"+onegeno+"_"):].replace(".csv","")} for f in onlyfiles])
    print(allpools)

    #Read all the files
    for i in range(len(allpools)):
        onepool=allpools[i]
        plotdatafile = "barseq_abundance/"+onepool["file"]
        print(plotdatafile)
        DATA = pd.read_csv(plotdatafile)
        onepool["data"] = DATA
        onepool["hasgene"] = selected_gene in set(DATA["gene"].tolist())

    #only keep those with the selected gene
    allpools = [p for p in allpools if p["hasgene"]]

    #Decide plot locations
    ncol = 3
    nrow = int(math.ceil(len(allpools)/ncol))
    if nrow==0:
        nrow=1
    figtot = make_subplots(
                cols=ncol, rows=nrow,
                specs=[[{"type": "scatter"}]*ncol]*nrow)

    #how to color mice
    colorlist = pd.read_csv("colors.csv")["color"]
    color_discrete_map = dict(zip(["m"+str(i+1) for i in range(len(colorlist))], colorlist))

    #loop over all possible genotypes and pools
    figlist=[]
    coli=1
    rowi=1
    paneli=1
    for onepooli,onepool in enumerate(allpools):
        fname = onepool["file"]
        poolname = onepool["name"]
        DATA = onepool["data"]

        list_mice = set(DATA["mice"].tolist())
        for onemouse in list_mice:
            usedat = DATA[DATA["gene"] == selected_gene].copy()
            usedat = usedat[usedat["mice"] == onemouse]
            hover_data = ["<br>".join([str(i)+":"+str(rec[i]) for d,i in enumerate(rec)])
                                     for rec in usedat.to_dict('records')]
            fig1 = go.Scatter(
                mode = 'lines+markers',
                x = usedat["day"],
                y = usedat["abundance"],
                marker_color = [color_discrete_map[c] for c in usedat['mice']],
                line_color = color_discrete_map[onemouse],
                hovertext = hover_data, showlegend=False
            )
            figtot.add_trace(fig1,row=rowi, col=coli)

        figtot.update_xaxes(title_text="Day, "+poolname, row=rowi, col=coli)
        figtot.update_yaxes(title_text="BC abundance(%)", row=rowi, col=coli)
        coli=coli+1
        paneli=paneli+1
        if coli>ncol:
            coli=1
            rowi=rowi+1

    figtot.update_layout( autosize= False, width = 1200, height = nrow*300, margin={'t':0, 'b':0,'l':0, 'r':0})
    return figtot







# run the app on "python app.py";
# default port: 8050
if __name__ == '__main__':
    app.run_server(host='127.0.0.1',debug = True, port = 15590)

app = dash.Dash(__name__)
#viewer.show(app)






