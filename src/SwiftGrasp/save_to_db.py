# ToDo: pull, ETL and save data to postgresql
import datetime

# import pickle
# import numpy as np
import pandas as pd

# from PIL import Image
# import sys
import psycopg2

# from apscheduler.schedulers.background import BackgroundScheduler
# import time
import os
from sqlalchemy import create_engine
import streamlit as st

# Set parameters
user = st.secrets["postgres"]["user"]
password = st.secrets["postgres"]["password"]
database = st.secrets["postgres"]["database"]
port = st.secrets["postgres"]["port"]
engine = create_engine(f"postgresql://{user}:{password}@localhost:{port}/{database}")


def create_table(table_name):
    try:
        conn = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host="localhost",
            port=port,
        )
    except Exception:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    try:
        cur.execute(
            f"""
        create table {table_name}(
            img_id            bigserial PRIMARY KEY,
            ticker            text,
            frequency         text,
            statement_date	  timestamp,
            png				  bytea
        );
        """
        )
    except Exception:
        print(f"can't create the {table_name} in database!")

    conn.commit()  # <--- makes sure the change is shown in the database
    conn.close()
    cur.close()


def insert_table(df, table_name):
    """
    when append, the column names should be the same
    as in sql table, orders don't matter
    """
    df.to_sql(
        table_name,
        engine,
        schema="public",
        chunksize=1000,
        index=False,
        if_exists="append",
    )


def prepare_df(cach_folder: str):
    """From pandas df insert to postgresql"""
    print(datetime.datetime.now())

    df = pd.DataFrame(
        {"filename": [i for i in os.listdir(cach_folder) if i.endswith(".png")]}
    )
    df["ticker"] = df["filename"].str.split("_").str[3]
    df["frequency"] = df["filename"].str.split("_").str[4]
    df["statement_date"] = df["filename"].str.split("_").str[5].str.split(".").str[0]
    df["statement_date"] = pd.to_datetime(df["statement_date"])
    df["png"] = df["filename"].apply(
        lambda x: open(os.path.join(cach_folder, x), "rb").read()
    )

    return df.drop("filename", axis=1)


if __name__ == "__main__":
    cach_folder = "./cached"
    df = prepare_df(cach_folder)
    print(df.head())
    print(df.dtypes)

    table_name = "structure_change_plots"
    # create_table(table_name)

    insert_table(df, table_name)
    print(datetime.datetime.now())

    # # save summary
    # table_name = "structure_change_summary"
    # for i in os.listdir(cach_folder):
    #     if i.endswith("summary.p"):
    #         ticker = i.split('_')[2]
    #         freq = i.split('_')[3]
    #         df = pickle.load(open(os.path.join(cach_folder,i),'rb')).reset_index()
    #         df.insert(0,'ticker',ticker)
    #         df.insert(1,'frequency',freq)
    #         print(df.head(1))
    #         insert_table(df, table_name)
