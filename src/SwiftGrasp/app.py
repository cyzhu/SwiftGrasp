# from markdown import markdown
import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import os
import pickle
cach_folder = './cached'

import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.insert(0, '../src/SwiftGrasp')
from utils import *
from plot_helper import line_plots


st.title("SwiftGrasp")
st.write("A web app about a company's performance and people's opinion on it")

st.text("\n")
st.write("Disclaimer: The Content is for informational purposes only, not for investment advice.")
st.text("\n")

st.subheader('1. Input a ticker here')
st.write("Choose one of the two options below to start.")
st.markdown("_Notes: If you have inputs on both, the text input from **Option 2** will be used._")
st.text("\n")

ticker_selectbox=st.selectbox(label = 'Option 1: Choose a ticker from the dropdown list'
                ,options=['AAPL','GOOGL','AMZN','MSFT','META','TSLA','NFLX','NVDA','WFC', 'BAC', 'C','^GSPC','^IXIC','^DJI']
                )

ticker_text = st.text_input(label = "Option 2: Input a ticker here, example: AAPL, MSFT, GOOGL, etc."
    ,value = "")

if ticker_text == "":
    ticker = ticker_selectbox
else:
    ticker = ticker_text

# check validaty of the ticker
ct = CheckTicker(ticker, type='both')

if not (ct.has_stock or ct.has_statement):
    raise ValueError(f"This ticker {ticker} doesn't have any data. Please check the spelling or choose another ticker.")

first_trade_date = ct.get_first_trade_date()

if ct.has_stock:
    has_stock = 'Yes'
else:
    has_stock = 'No'

if ct.has_statement:
    has_statement = 'Yes'
else:
    has_statement = 'No'

st.markdown("#### Request summary")
st.markdown(f"You chose ticker **{ticker}**")
st.markdown(f"* Stock data: {has_stock}")
st.markdown(f"* Statement data: {has_statement}")
st.markdown(f"* First trade date: {first_trade_date}")

st.subheader('2. Financial statement data')

# load data
@st.cache(allow_output_mutation=True)
def load_data(filename:str):
    with open(os.path.join(cach_folder, f"{filename}.p"), 'rb') as pf:
        obj = pickle.load(pf)
    return obj

#ToDo: need to check irregular ticker name for file name
fname = f"fsd_{ticker}"
if os.path.exists(os.path.join(cach_folder, f"{fname}.p")):
    fsd = load_data(fname)
else:
    fsd = FinancialStatementData(ticker)
    with open(os.path.join(cach_folder, f"{fname}.p"), 'wb') as pf:
        pickle.dump(fsd,pf,protocol=4)

df_financial = fsd.get_all_data()

st.write(df_financial)

# make some plots
options0=st.multiselect(label = 'Choose financial data to display:'
                ,options=[col for col in df_financial.columns if col !=fsd._colname_date]
                ,default = ['totalAssets','cash','netIncome'])

op10 = [col for col in options0 if max(df_financial[col]) > 1e6]
op20 = [col for col in options0 if max(df_financial[col]) <= 1e6]

st.bokeh_chart(line_plots(df_financial,fsd._colname_date,op10,op20), use_container_width=True)

st.subheader("3. Stock data")

today = datetime.datetime.today().date()
first_trade_date_format = datetime.datetime.strptime(first_trade_date, '%Y-%m-%d').date()

start_time, end_time = st.slider("Select the time range (inclusive) of the stock:"
    ,min_value = first_trade_date_format
    ,max_value = today
    ,value=(max(today-relativedelta(years=3),first_trade_date_format), today)
    )

st.write("You selected datetime between:", start_time,' and ', end_time)

stock_frequency = st.radio(
        "Choose the frequency for the stock data",
        ('daily', 'weekly', 'monthly')
        )
resample_dict = {
    'daily':'D'
    ,'weekly':'W'
    ,'monthly':'MS'
    }

sd = StockData(ticker, start_date = start_time.strftime('%Y-%m-%d'),end_date = end_time.strftime('%Y-%m-%d'), frequency = stock_frequency)
df_stock = sd.get_stock()

st.write(df_stock.head())

df_stock = df_stock.loc[:,[fsd._colname_date,'close']]


df_stock_fill = df_stock.drop_duplicates(subset=fsd._colname_date, keep='last').set_index(fsd._colname_date).sort_index()
df_stock_fill = df_stock_fill.resample(resample_dict.get(stock_frequency)).fillna('nearest')

change_dt_list = df_financial[fsd._colname_date].dt.strftime('%Y-%m-%d').to_list()

st.subheader('4. Structural change - causal inference')


fname = f'struc_change_{ticker}'
delete_if_exists = True

if os.path.exists(os.path.join(cach_folder, f"{fname}.p")) and delete_if_exists:
    os.remove(os.path.join(cach_folder, f"{fname}.p"))

if os.path.exists(os.path.join(cach_folder, f"{fname}.p")):
    sc = load_data(fname)
else:
    sc = StructuralChange(df_stock_fill, change_dt_list[:2])
    sc.analyze()
    # with open(os.path.join(cach_folder, f"{fname}.p"), 'wb') as pf:
    #     pickle.dump(sc,pf,protocol=4)

st.write("Structural change summary")
st.write(sc._df_summary)

struc_chg_selectbox=st.selectbox(label = 'Select a possible change date to view the plots'
                ,options=sc._ci_dict.keys()
                )

ci_select = sc._ci_dict.get(struc_chg_selectbox)
fig = plt.gcf()
ci_select.plot(show=False)
st.pyplot(fig)