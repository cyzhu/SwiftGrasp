# from markdown import markdown
import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
# import matplotlib.pyplot as plt

# import pandas as pd
# import numpy as np
import os
import pickle


import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.insert(0, '../src/SwiftGrasp')
from utils import *
from plot_helper import line_plots, line_bar

cach_folder = './cached'
# date colname is hard coded here, should think about
# possible inconsistency in the future
date_col = 'formatted_date'


st.title("SwiftGrasp")
st.write("A web app about a company's performance and people's \
    opinion on it")

st.text("\n")
st.write("Disclaimer: The Content is for informational purposes \
    only, not for investment advice.")
st.text("\n")

st.subheader('1. Input a ticker here')
# get user input
st.write("Choose one of the two options below to start.")
st.markdown("_Notes: If you have inputs on both, the text input \
    from **Option 2** will be used._")
st.text("\n")

ticker_selectbox=st.selectbox(
    label = 'Option 1: Choose a ticker \
            from the dropdown list'
    ,options=['AAPL','GOOGL','AMZN','MSFT','META',
        'TSLA','NFLX','NVDA','WFC', 'BAC', 'C',
        '^GSPC','^IXIC','^DJI']
    )

ticker_text = st.text_input(label = "Option 2: Input a ticker \
    here, example: AAPL, MSFT, GOOGL, etc."
    ,value = ""
    )

if ticker_text == "":
    ticker = ticker_selectbox
else:
    ticker = ticker_text

# check validaty of the ticker
ct = CheckTicker(ticker, type='both')

ticker = ct.ticker

if not (ct.has_stock or ct.has_statement):
    st.markdown(f"_This ticker {ticker} doesn't have any data.\
        Please check the spelling or choose another ticker._")
else:
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
    with open(os.path.join(cach_folder, f"{filename}.p"), 'rb') \
        as pf:
        obj = pickle.load(pf)
    return obj

if ct.has_statement:
    fd_frequency = st.radio(
            "Choose the frequency for the financial statement data",
            ('quarterly', 'annual')
            )
    fd_frequency_dict = {
        'quarterly':'Q'
        ,'annual':'Y'
        }
    fd_frequency_abbr = fd_frequency_dict.get(fd_frequency)
    
    #ToDo: need to check irregular ticker name for file name
    fname = f"fsd_{ticker}_{fd_frequency_abbr}"
    if os.path.exists(os.path.join(cach_folder, f"{fname}.p")):
        fsd = load_data(fname)
    else:
        fsd = FinancialStatementData(ticker, frequency=fd_frequency)
        with open(os.path.join(cach_folder, f"{fname}.p"), 'wb') as pf:
            pickle.dump(fsd,pf,protocol=4)

    df_financial = fsd.get_all_data()

    change_dt_list = df_financial[
        date_col].dt.strftime('%Y-%m-%d').to_list()

    st.write(df_financial)

    # make some plots
    options0=st.multiselect(label = 'Choose financial data to display:'
                    ,options=[col for col in df_financial.columns 
                        if col !=date_col]
                    ,default = ['totalAssets','cash','netIncome'])

    op10 = [col for col in options0 if max(df_financial[col]) > 1e6]
    op20 = [col for col in options0 if max(df_financial[col]) <= 1e6]

    st.bokeh_chart(
        line_plots(df_financial,date_col,op10,op20), 
        use_container_width=True
    )
else:
    change_dt_list = None
    st.markdown("_The ticker you chose doesn't have financial statement \
        data. Therefore nothing will be shown in this section._")

st.subheader("3. Stock data")

if ct.has_stock:
    today = datetime.datetime.today().date()
    first_trade_date_format = datetime.datetime.strptime(
        first_trade_date, 
        '%Y-%m-%d').date()

    start_time, end_time = st.slider("Select the time range (inclusive) \
        of the stock:"
        ,min_value = first_trade_date_format
        ,max_value = today
        ,value=(
            max(today-relativedelta(years=3),first_trade_date_format),
            today
            )
        )

    st.write("You selected datetime between:", start_time,' and ', 
        end_time)

    stock_frequency = st.radio(
            "Choose the frequency for the stock data",
            ('daily', 'weekly', 'monthly')
            )
    resample_dict = {
        'daily':'D'
        ,'weekly':'W'
        ,'monthly':'MS'
        }

    sd = StockData(
        ticker, 
        start_date = start_time.strftime('%Y-%m-%d'),
        end_date = end_time.strftime('%Y-%m-%d'), 
        frequency = stock_frequency
    )
    df_stock_all = sd.get_stock()


    # make some plots
    options_stock=st.multiselect(label = 'Choose stock data to display:'
                    ,options=['high','low','open','close','volume']
                    ,default = ['open','close','volume'])

    if 'volume' in options_stock:
        col_y2 = 'volume'
    else:
        col_y2 = None
    st.bokeh_chart(
        line_bar(
            df_stock_all,
            date_col,
            [col for col in options_stock if col != 'volume'],
            col_y2,
            title = 'Stock Info',
            vline_list = change_dt_list
            ), 
        use_container_width=True
    )

    df_stock = df_stock_all.loc[:,[date_col,'close']]


    df_stock_fill = df_stock.drop_duplicates(
        subset=date_col, 
        keep='last').set_index(date_col).sort_index()
    df_stock_fill = df_stock_fill.resample(
        resample_dict.get(stock_frequency)
        ).fillna('nearest')
else:
    st.markdown("_The ticker you chose doesn't have stock \
        data. Therefore nothing will be shown in this section._")


st.subheader('4. Structural change - causal inference')

if ct.has_stock and ct.has_statement:
    fname = f'struc_change_{ticker}_{fd_frequency_abbr}_summary'
    if os.path.exists(os.path.join(cach_folder, f"{fname}.p")):
        sc_summary = load_data(fname)

        st.write("Structural change summary")
        st.write(sc_summary)

        struc_chg_selectbox=st.selectbox(
            label = 'Select a possible change \
                date to view the plots'
            ,options=change_dt_list
            )

        fname = f'struc_change_{ticker}_{fd_frequency_abbr}_fig{struc_chg_selectbox}'
        fig = load_data(fname)
        st.pyplot(fig)
    else:
        st.markdown("_The ticker you chose hasn't been processed yet. \
                It was just submitted and should be ready in ~10 \
                minutes. Please check again later._")
        #ToDo: insert a request to process the data to database here
        # currently it's mannualy run and saved in a manual manner
else:
    st.markdown("_The ticker you chose either not have stock data or \
        not financial statement data or both. Therefore it won't have \
        a analysis on the relationship of stock and financial statement._")


st.subheader('Contact')
st.markdown("For bugs or data issues, please email \
    [CZhu2@my.harrisburgu.edu](mailto:CZhu2@my.harrisburgu.edu)")

