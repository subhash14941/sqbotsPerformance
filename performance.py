import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import requests,json

pnl_url=r'http://performance.squareoffbots.com/assets/json/sqbots_allData_21052021.json'
cap_url=r'http://performance.squareoffbots.com/assets/json/newCAp21052021.json'

pnl_data=requests.get(pnl_url)
cap_data=requests.get(cap_url)

pnl_df_t=pd.DataFrame.from_dict(json.loads(pnl_data.text))
cap_df_t=pd.DataFrame.from_dict(json.loads(cap_data.text))

pnl_df=pnl_df_t.T
cap_df=cap_df_t.T

st.title("**♟**Explore E-com dashboard**♟**")
st.write("Here, you can see the demo of a simple web-app dashboard."
"It will show you general information such as your sales and revenue for a specific "
"ecom-platform on which you sell your products.")


layout = go.Layout(
title= "<b>Revenue and cost of Tiki, Sendo & Shopee</b>",
paper_bgcolor = 'rgb(248, 248, 255)',
plot_bgcolor = 'rgb(248, 248, 255)',
barmode = "stack",
xaxis = dict(domain=[0, 0.5], title="Time", linecolor="#BCCCDC",
showspikes=True,spikethickness=2,spikedash="dot",spikecolor= "violet",spikemode="across",),
yaxis= dict(title="Revenue",linecolor="#021C1E"),
xaxis2= dict(domain=[0.6, 1],title="Time",linecolor="#021C1E", showspikes=True, spikethickness= 2, spikedash= "dot",spikecolor="violet",spikemode="across",),
yaxis2 = dict(title="Cost",anchor="x2",linecolor="#021C1E")
)

data=[]          
platform="Tiki"
line_chart= go.Scatter(x=pnl_df.index, y=pnl_df['BNF Straddle'], marker_color="rgb(76, 76, 230)", legendgroup=platform, name=platform )

data.append(line_chart)


fig= go.Figure(data=data, layout=layout)
fig2=go.Figure(data=[go.Table(
    header=dict(values=['Date','BSS'],
                fill_color='white',
                align='left'),
    cells=dict(values=[pnl_df.index,pnl_df['BNF Straddle']],
               fill_color='white',
               align='left'))])
st.plotly_chart(fig)
st.plotly_chart(fig2)