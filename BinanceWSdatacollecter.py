"""
Created on Mon June 06 18:03:30 2018

@author: techietrader
"""


from binance.client import Client
import pandas as pd
import csv
import datetime as dt
import requests
import time
import pandas
from binance.websockets import BinanceSocketManager
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
pd.options.mode.chained_assignment = None
import logging
logging.basicConfig()



'''
A small function to extract API and Secret Api keys from the api_key.txt

'''

def get_api(filename):
    try:
        with open(filename,'r') as api_key:
            return eval(api_key.read())
    except Exception as e:
        print e
        print 'Write the keys in string formats. For eg: ["fjkdslfdslfds"]'

keys = get_api('api_key.txt')
    

client = Client(keys[0], keys[1])


# Lets read the contents of the Tokens.dat
with open('Tokens.dat','r') as tokens:
    mess=tokens.read()
    instruments=eval(mess) 

# List of all the traded tokens on Binance
total_traded_tokens = [i['symbol'] for i in client.get_all_tickers()]



'''
The below command allows us to throw an output on console to notify the user of the invalid token in the 
Tokens.dat file
'''

valid_tokens = []
for token in instruments:
    if token not in total_traded_tokens:
        print '"{}" ,Doesnt seem to be a valid pair.'.format(token)
        print 'However we will continue fetching data for other valid pairs'
    else:
        valid_tokens.append(token)



# Lets create as many instances  as the number of tokens in our valid_tokens list 
instance_list = ['bm'+str(index) for index, instrument in enumerate(valid_tokens)]
'''
Output-
['bm0', 'bm1', 'bm2', 'bm3', 'bm4', 'bm5', 'bm6', 'bm7', 'bm8', 'bm9']
'''

'''
Please Note- If you add new token/pair to Tokens.dat after creating the instance_list, 
make sure you rerun the above code
'''


# Creating a CSV file to which we will later append rows by calling process_message function
with open('SymbolValues.csv','w') as f:
    w = csv.writer(f)
    w.writerow(['Date','Dt in Milliscs','Symbol','BestBid','BidQuantity','BestAsk','AskQuantity'])



# The function writes new rows to a csv file

def process_message(msg):
    #print msg
    ''' 
    Output 
    Date	                 Dt in Milliscs	Symbol	   BestBid	   BidQuantity	BestAsk	AskQuantity
    06/08/2018  3:05:41 AM 1.5335E+12	       BTCUSDT	7041.62	0.496764	    7045.59	 0.496045
    06/08/2018  3:05:42 AM 1.5335E+12	       ETHUSDT	411.68	    3.03471	    411.78     0.06477 
    
    msg Format
    {u'A': u'197.92000000', u'C': 1533544494324L, u'B': u'94.11000000', u'E': 1533544494323L, 
    u'F': 14569374, u'L': 14592416, u'O': 1533458094324L, u'Q': u'94.11000000', 
    u'P': u'2.420', u'a': u'13.64730000', u'c': u'13.63720000', u'b': u'13.63710000', u'e': u'24hrTicker', 
    u'h': u'13.97500000', u'l': u'13.27000000', u'o': u'13.31500000', u'n': 23043, u'q': u'14206367.56719700',
    u'p': u'0.32220000', u's': u'BNBUSDT', u'w': u'13.59595774', u'v': u'1044896.42000000', 
    u'x': u'13.29000000'}
    
    {
                "e": "24hrTicker",  # Event type
                "E": 123456789,     # Event time
                "s": "BNBBTC",      # Symbol
                "p": "0.0015",      # Price change
                "P": "250.00",      # Price change percent
                "w": "0.0018",      # Weighted average price
                "x": "0.0009",      # Previous day's close price
                "c": "0.0025",      # Current day's close price
                "Q": "10",          # Close trade's quantity
                "b": "0.0024",      # Best bid price
                "B": "10",          # Bid bid quantity
                "a": "0.0026",      # Best ask price
                "A": "100",         # Best ask quantity
                "o": "0.0010",      # Open price
                "h": "0.0025",      # High price
                "l": "0.0010",      # Low price
                "v": "10000",       # Total traded base asset volume
                "q": "18",          # Total traded quote asset volume
                "O": 0,             # Statistics open time
                "C": 86400000,      # Statistics close time
                "F": 0,             # First trade ID
                "L": 18150,         # Last trade Id
                "n": 18151          # Total number of trades
            }
    '''
    try:   
        with open('SymbolValues.csv','ab')as f:       
            w = csv.writer(f)
            w.writerow([dt.datetime.now(),msg['C'],msg['s'],msg['b'],msg['B'],msg['a'], msg['A']])
    except (IOError, pandas.errors.ParserError):
        print 'Seems you opened the csv file'
        print 'Not a problem. However once you close it the recording of data will begin again'
        time.sleep(15)    
            
    return
    


'''
The Below instances are the pairs for which we want data to be collected. You can create new instances and 
add new pairs as per your preferences
'''


for instance, instrument in zip(instance_list,instruments):
    instance = BinanceSocketManager(client)
    instance.start_symbol_ticker_socket(instrument,process_message)
    instance.start()
    



    


print "Processed 0 ticks."
while True:
    count = len(pd.read_csv('SymbolValues.csv'))
    if count != 0 and count % 1000 == 0 :
        print "Processed {} ticks.".format(count)
        time.sleep(10)

