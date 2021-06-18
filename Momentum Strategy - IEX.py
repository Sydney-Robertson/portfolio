# API = Application Programming Interface
# IEX Cloud API
# POST: Adds data to the database exposed by the API (create only)
# PUT: Adds and overwrites data in the database exposed by the API (create or replace)
# DELETE: Deletes data from API

import numpy as np
import pandas as pd
import requests
import math
from scipy.stats import percentileofscore as score
import xlsxwriter

stocks = pd.read_csv('sp_500_stocks.csv')
#print(stocks)

from secrets import IEX_CLOUD_API_TOKEN

symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
#print(api_url)

data = requests.get(api_url).json()
#print(data)

#print(data['year1ChangePercent'])


# Function sourced from 
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]   
        
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

# Build a Better (and more realistic) Momentum Strategy

# hqm: high quality momentum

hqm_columns = [
    'Ticker',
    'Price',
    'Number of Shares to Buy',
    'One-Year Price Return',
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'HQM Score'
]

hqm_dataframe = pd.DataFrame(columns=hqm_columns)
#print(hqm_dataframe)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        hqm_dataframe = hqm_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']['latestPrice'],
                    'N/A',
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month6ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month3ChangePercent'],
                    'N/A',
                   data[symbol]['stats']['month1ChangePercent'],
                    'N/A',
                    'N/A'
                ],
                index=hqm_columns),
                ignore_index=True
        )
    
#print(hqm_dataframe)

# Calculating Momentum Percetiles

time_periods = [
                'One-Year',
                'Six-Month',
                'Three-Month',
                'One-Month'
                ]
'''
for row in hqm_dataframe.index:
    for time_period in time_periods:
        hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'], hqm_dataframe.loc[row, f'{time_period} Price Return'])        
'''

for row in hqm_dataframe.index:
    for time_period in time_periods:
        if hqm_dataframe.loc[row, f'{time_period} Price Return'] == None:
            hqm_dataframe.loc[row, f'{time_period} Price Return'] = 0

for row in hqm_dataframe.index:
    for time_period in time_periods:
        change_col = f'{time_period} Price Return'
        percentile_col = f'{time_period} Return Percentile'
        #hqm_dataframe.loc[row, percentile_col] = 0
        hqm_dataframe.loc[row, percentile_col] = score(hqm_dataframe[change_col], hqm_dataframe.loc[row, change_col])

#print(hqm_dataframe)

# Calculating the HQM Score: Arithmetic Mean 

from statistics import mean

for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)

#print(hqm_dataframe)

# Selecting the 50 Best Momentum Stocks

hqm_dataframe.sort_values('HQM Score', ascending=False, inplace=True)
#print(hqm_dataframe)

hqm_dataframe = hqm_dataframe[:50]
hqm_dataframe.reset_index(drop=True, inplace=True)


def portfolio_input():
    global portfolio_size
    portfolio_size = input('Enter the size of your Portfolio: ')

    try:
        float(portfolio_size)
    except:
        print('That is not a number \n Please try again:')
        portfolio_size = input('Enter the size of your Portfolio: ')

portfolio_input()
print(portfolio_size)

position_size = float(portfolio_size)/len(hqm_dataframe.index)
for i in hqm_dataframe.index:
    hqm_dataframe.loc[i,'Number of Shares to Buy'] = math.floor(position_size/hqm_dataframe.loc[i, 'Price'])

print(hqm_dataframe)

writer = pd.ExcelWriter('Momentum_strat.xlsx', engine='xlsxwriter')
hqm_dataframe.to_excel(writer, sheet_name='mom_strat', index=False)

writer.save()
# Could set-up formatting dictionary, but its easier on excel for obvious reasons

#hqm_dataframe['amount'] = hqm_dataframe['Price']*hqm_dataframe['Number of Shares to Buy']

#print(hqm_dataframe)

