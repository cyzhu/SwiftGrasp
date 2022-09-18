import pandas as pd
import os

folder_resource = "./src/SwiftGrasp/resources/"

def load_nasdaq():
    filename = 'nasdaq-listed.csv'
    df1 = pd.read_csv(os.path.join(folder_resource,filename))
    df1 = df1.loc[:,['Symbol','Company Name','Security Name']]
    df1['Exchange'] = 'NASDAQ'

    return df1

def load_other():
    # nyse listing are totally contained by other-listed so no need to load
    filename = 'other-listed.csv'
    df3 = pd.read_csv(os.path.join(folder_resource,filename))
    df3 = df3.loc[:,['CQS Symbol','Company Name','Security Name']]
    df3.rename(columns = {'CQS Symbol':'Symbol'}, inplace=True)
    df3['Exchange'] = 'other'

    return df3

def process_df(df1:pd.DataFrame, df2:pd.DataFrame):
    df = pd.concat([df1, df2], ignore_index=True)
    
    gb = df.groupby('Company Name')['Symbol'].count()
    gb = gb.reset_index()
    list_dup_name = gb.loc[gb['Symbol']>3,'Company Name'].to_list()
    
    df['company name length'] = df['Company Name'].str.len()
    list_abbr_name = df.loc[df['company name length']<5,'Company Name'].to_list()

    full_set = set(list_abbr_name+list_dup_name)

    df.loc[df['Company Name'].isin(full_set),'Company Name'] = df.loc[df['Company Name'].isin(full_set),'Security Name']
    
    return df.drop(['Security Name','company name length'], axis=1)


if __name__ == '__main__':
    df1 = load_nasdaq()
    df3 = load_other()
    df = process_df(df1, df3)
    df.to_csv(os.path.join(folder_resource,"processed_company_names.csv"), index=None)
