import requests
from bs4 import BeautifulSoup
import time
#import csv



symbol = 'BHP.AX'

def priceTracker():
    #time.sleep(1)
    url = f'https://au.finance.yahoo.com/quote/{symbol}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    #print(soup)
    price = soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
    return price

while True:
    print(f'Current Price of {symbol} -15m: ' + priceTracker())


#def processing_loop(csvfile):
#    csv_writer = csv.writer(csvfile)
#    csv_writer.writerow(['symbol', 'price'])
#
#    while True:
#        url = f'https://au.finance.yahoo.com/quote/{symbol}/'
#        response = requests.get(url)
#        soup = BeautifulSoup(response.text, 'lxml')
#        #print(soup)
#        price = soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
#        csv_writer.writerow([symbol, price])
#        csvfile.flush()
#        print(price)
#        time.sleep(1)
#
#with open('BHP.csv', 'w') as csvfile:
#    processing_loop(csvfile)


