import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import requests,json
from datetime import datetime
import plotly.express as px
from returnsDf import agg_df
pnl_url=r'http://performance.squareoffbots.com/assets/json/sqbots_allData_21052021.json'
cap_url=r'http://performance.squareoffbots.com/assets/json/newCAp21052021.json'

pnl_data=requests.get(pnl_url)
cap_data=requests.get(cap_url)

pnl_df_t=pd.DataFrame.from_dict(json.loads(pnl_data.text))
cap_df_t=pd.DataFrame.from_dict(json.loads(cap_data.text))

pnl_df=pnl_df_t.T
cap_df=cap_df_t.T

query_params = st.experimental_get_query_params()
botName = query_params["bot"][0] if "bot" in query_params else "bss"



botNameDic={"orb":"ORB","rsi":"RSI","it":"Intraday Trend","sh":"StopHunt","grb":"GRB","orb2pm":"ORB2pm","pcr":"NiftyOptionSelling","lapp":"Learnapp","bss":"BNF Straddle","nss":"Nifty Straddle","bos":"BNFOptionSelling","grbo":"GRB Options","bssr":"BNF Strangle","mlb":"ML Bot","bnfmon":"BNF ORB"}

botCapitalDic={"orb":50000,"rsi":50000,"it":50000,"sh":50000,"grb":200000,"orb2pm":200000,"pcr":200000,"lapp":200000,"bss":200000,"nss":200000,"bos":200000,"grbo":100000,"bssr":200000,"bnfmon":100000,"mlb":400000}


eq_bots=["orb","rsi","sh","it"]
botFullName=botNameDic[botName]
botCapital=botCapitalDic[botName]
strat_pnl_Df=pnl_df[[botFullName]]
strat_pnl_Df.dropna(inplace=True)
strat_cap_df=cap_df[[botFullName]]

#returns calculation
strat_df=agg_df(strat_pnl_Df,strat_cap_df)

##PNL plot
strat_df['pdTime']=pd.to_datetime(strat_df.index,format="%Y-%m-%d")
strat_df.sort_values('pdTime',inplace=True)
strat_df[botFullName+'_adj_PnL']=(botCapital/100)*strat_df[botFullName+' Returns'].astype(float)
strat_df["Time"]=strat_df.index
strat_df['PNL']=strat_df[botFullName+'_adj_PnL']
strat_df['cum_pnl']=strat_df[botFullName+'_adj_PnL'].cumsum()


##DRAWDOWN
drawdown_df=strat_df.copy()
drawdown_df.reset_index(drop=True,inplace=True)
drawdown_df['max_value_so_far']=drawdown_df['cum_pnl'].cummax()
drawdown_df['drawdown']=drawdown_df['cum_pnl']-drawdown_df['max_value_so_far']
max_drawdown=drawdown_df['drawdown'].min()
##Strategy statistics
stats_Df=pd.DataFrame(columns=["Total Days","Winning Days","Losing Days","Winning Accuracy(%)","Max Profit","Max Loss","Max Drawdown","Average Profit on Win Days","Average Profit on loss days","Average Profit Per day","Net profit","net Returns (%)"])
total_days=len(strat_df)
win_df=strat_df[strat_df[botFullName+'_adj_PnL'].astype('float')>0]
lose_df=strat_df[strat_df[botFullName+'_adj_PnL'].astype('float')<0]
noTrade_df=strat_df[strat_df[botFullName+'_adj_PnL'].astype('float')==0]

win_days=len(win_df)
lose_days=len(lose_df)

win_ratio=win_days*100.0/(lose_days+win_days)
max_profit=strat_df[botFullName+'_adj_PnL'].max()
max_loss=strat_df[botFullName+'_adj_PnL'].min()

# max_drawdown=0
win_average_profit=win_df[botFullName+'_adj_PnL'].sum()/win_days
loss_average_profit=lose_df[botFullName+'_adj_PnL'].sum()/lose_days

total_profit=strat_df[botFullName+'_adj_PnL'].sum()
average_profit=total_profit/total_days

net_returns=strat_df[botFullName+' Returns'].sum()

results_row=[total_days,win_days,lose_days,win_ratio,max_profit,max_loss,max_drawdown,win_average_profit,loss_average_profit,average_profit,total_profit,net_returns]

results_row=[results_row[i] if i<3 else round(results_row[i],2) for i in range(len(results_row)) ]
stats_Df.loc[0,:]=results_row
t_stats_Df=stats_Df.T
t_stats_Df.rename(columns={0:''},inplace=True)
fig=px.line(strat_df, x="Time", y='cum_pnl', title=botFullName+' PNL',width=800, height=400)
dd_fig=px.line(drawdown_df,x="Time",y="drawdown", title=botFullName+' PNL',width=800, height=400)

strat_df['month']=strat_df['pdTime'].apply(lambda x:x.strftime('%b,%Y'))

month_groups=strat_df.groupby('month',sort=False)['PNL'].sum()
# month_groups['pdTime']=pd.to_datetime(month_groups.index,format='%b,%Y')

# month_groups.sort_values('pdTime',inplace=True)





##last 30 days pnl
strat_df=strat_df.reindex(strat_df.index[::-1])


if botName in eq_bots:
    capital_used_appendum=''
else:
    
    capital_used_appendum=' per Lot'
   

st.title("**♟**SQUAREOFF BOTS PERFORMANCE**♟**")
st.write("**LIVE PERFORMANCE OF "+botFullName+"**")
st.write("**[Capital used is "+str(botCapital)+capital_used_appendum+"]**")
if botCapital>50000:
    st.write("**(Capital used from July 2021 is "+str(1.5*botCapital)+capital_used_appendum+")**")
st.write("Net ROI : "+str(results_row[-1])+"%")
st.write("**Statistics**")
st.table(t_stats_Df)
st.write("**PNL Curve**")
st.plotly_chart(fig)
st.write("**Drawdown Curve**")
st.plotly_chart(dd_fig)
st.write("**Month-wise PNL**")
st.table(month_groups)
st.write("**Date-wise PNL (Last 30 Days)**")
st.table(strat_df['PNL'][:30])




##TABLE
# fig2=go.Figure(data=[go.Table(
#     header=dict(values=['Date','BSS'],
#                 fill_color='white',
#                 line_color='black',
               
#                 align='left'),
#     cells=dict(values=[strat_df.index,strat_df[botFullName+'_adj_PnL']],
#                fill_color='white',
               
             
#                align='left'))])
# st.plotly_chart(fig2)