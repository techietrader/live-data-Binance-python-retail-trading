"""
Created on Mon June 18 18:03:30 2018

@author: techietrader
"""

from binance.client import Client
from binance.websockets import BinanceSocketManager
import pandas as pd
import csv
import datetime as dt
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
pd.options.mode.chained_assignment = None
import logging
logging.basicConfig()
import json

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


'''
Getting the token names that we wish to trade
''' 

with open('Tokens.dat','r') as tokens:
    mess1=tokens.read()
    scrips=eval(mess1)
 

'''
Lets define a small function that will extract tokens from pairs. This we want to know our indiviudal token names
to get their respective balances.
For eg- If our trading pair is 'BTCUSDT', It will extract 'BTC' and 'USDT' out of it and stores it as seperate 
elements in the list

Currently we are writing only for USDT and BTC pegged pairs.
'''
def tokens(my_list):
    # my_list = ['BTCUSDT', 'ETHBTC', 'ADAUSDT']
    tokens = [scrip.split('USDT')[0] for scrip in my_list]
    # tokens = ['BTC','ETHBTC', 'ADA']    
    tokens = [scrip.split('BTC')[0] for scrip in tokens]
    # tokens = ['', 'ETH', 'ADA']
    tokens.extend(['BTC','USDT'])
    tokens = list(set(tokens)) # Removes Duplicate    
    tokens.remove('')
    return tokens # ['USDT', 'ETH', 'BTC', 'ADA']



tokens_list = tokens(scrips)
'''
Binance has placed some constraints on the Minimum quantity per trade and also on the minimum total value of 
trade which we call Minimum notional Value and these values are unique and dissimilar for tokens. We need to 
fetch these values and store it to compare them before we make trade.
Thus we create Dictionary object called thresholdRules to save these values.

'''

thresholdRules={}

for item in scrips:
    thresholdRules[item]={'minQty':0.0,'minNotional':0.0} # Initiating with 0.0
    thresholdRules[item]['minQty']=client.get_symbol_info(symbol=item)['filters'][1]['minQty']
    thresholdRules[item]['minNotional']=client.get_symbol_info(symbol=item)['filters'][2]['minNotional']
    
# get_symbol_info() helps us with a lot of data. Try it
# client.get_symbol_info(symbol = 'BNBBTC')    
# for more details- https://python-binance.readthedocs.io/en/latest/_modules/binance/client.html#Client.get_symbol_info
'''
Output of thresholdRules -
{'ADAUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.10000000'},
 'BCCUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.00001000'},
 'BNBUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.01000000'},
 'BTCUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.00000100'},
 'ETHBTC': {'minNotional': u'0.00100000', 'minQty': u'0.00100000'},
 'ETHUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.00001000'},
 'LTCUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.00001000'},
 'NEOUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.00100000'},
 'QTUMUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.00100000'},
 'XRPUSDT': {'minNotional': u'10.00000000', 'minQty': u'0.10000000'}}

'''

'''
Now Lets create an Order book where all of our previous orders stays. The required information should be 
Order_type, Order_Price, Order_Quantity, Order_Symbol, time and date.

Note - This is not a pending order book.
Note - The file recreates itself when you restart script. It will simply overirde your existing file.

'''

with open('Orders.csv','w') as f:
    w = csv.writer(f)
    w.writerow(['Datetime','Dt in Milliscs','Symbol','Type','Price','Quantity'])
    


def process_message(msg):
    global thresholdRules, scrips
    script_entry=[]
    account_balance={}
    script_total_balance={}

    #print("message type: {}".format(msg['e']))
    #print msg
    
    '''
    msg['e'] can take two values - 'outboundAccountInfo' [which shows all our account balances], 
    'executionReport' [ which shows details of a particular order that we send to the exchange].
    
    msg['X'] can take two values again - 'FILLED' [We sent order and the order was filled by matching an opposite
    order. This changes our account balances, 'NEW' [We sent order and order is still pending. This doesnot change
    account balances]. So we are more interested in msg['X'] == FILLED
    
    Here's the deal- Things are mostly event driven. What that means is whenever we call start_user_socket(), 
    when the state of our account changes by any particular event it sends us details. For eg-
    When we send a Buy/Sell Limit/Market Order ,etc.  
    
    '''
    '''
    message type: executionReport
    {u'C': u'null', u'E': 1533555014555L, u'F': u'0.00000000', u'I': 153900099, u'M': True, 
    u'L': u'0.00385100', u'O': 1533555014550L, u'N': u'BNB', u'P': u'0.00000000', u'S': u'SELL', 
    u'T': 1533555014550L, u'X': u'FILLED', u'Z': u'0.00192550', u'c': u'web_4ea9e2a604ab449ea5b0b71c1b9a7022', 
    u'e': u'executionReport', u'g': -1, u'f': u'GTC', u'i': 69071397, u'm': False, u'l': u'0.50000000', 
    u'o': u'LIMIT', u'n': u'0.00073968', u'q': u'0.50000000', u'p': u'0.00385100', u's': u'NEOBTC', 
    u'r': u'NONE', u't': 18007641, u'w': False, u'x': u'TRADE', u'z': u'0.50000000'}
    '''
    '''
    message type: outboundAccountInfo
    {u'b': 0, u'E': 1533555014556L, u'D': True, u'm': 10, u's': 0,
     u'u': 1533555014553L, u't': 10, u'W': True, 
     u'e': u'outboundAccountInfo', u'T': True}
     u'B': [{u'a': u'BTC', u'l': u'0.00000000', u'f': u'0.00192617'}, 
           {u'a': u'LTC', u'l': u'0.00000000', u'f': u'0.00000000'}, 
           {u'a': u'ETH', u'l': u'0.00000000', u'f': u'0.00000574'}, 
           {u'a': u'NEO', u'l': u'0.00000000', u'f': u'0.00072200'},
           the list goes on for all the tokens................}]
    
    
    '''
    # fetches the account balances of all the scrips that we are trading on
    if msg['e'] == 'outboundAccountInfo':
        script_entry= [item for item in msg['B'] for scrip in tokens_list  if item['a'] == scrip]
    
    elif msg['e'] == 'executionReport' and msg['X'] == 'FILLED':
        with open('Orders.csv','ab') as f:
            w = csv.writer(f)
            w.writerow([dt.datetime.now(),msg['E'],msg['s'],msg['S'],msg['L'],msg['q']])

    '''
    Orders.csv - Output
    Datetime	Dt in Milliscs	   Symbol	 Type	Price	Quantity
					
    06/08/2018 19:24	1.53356E+12	NEOBTC	 SELL	0.003849	0.49
    '''

    # Adding balance which is free and the one in the limit order
    script_total_balance={i['a'] : float(i['l']) + float(i['f']) for i in script_entry}
    
    # Exception Handling 
    if script_total_balance :
        pass
    else:
        script_total_balance = {client.get_asset_balance(asset=scrip)['asset'] : 
            float(client.get_asset_balance(asset=scrip)['free']) + 
            float(client.get_asset_balance(asset=scrip)['locked']) for scrip in tokens_list }
       
    '''
    Filters only those tokens where balance is not only greater than zero but also above our threshold rules.The rule currently 
    takes USDT related pairs but should more or less work on BTC pegged pairs too. Assume if balance is so low for USDT pair, that
    token also will not be eligible was BTC pegged pairs and viceversa.    
    '''

    for item in script_total_balance:
        if item == 'USDT':
            pass
        elif script_total_balance[item] > float(thresholdRules[item+'USDT']['minQty']) and \
             script_total_balance[item] * float(client.get_ticker(symbol=item+'USDT') \
             ['lastPrice']) >  float(thresholdRules[item+'USDT']['minNotional']):
                 account_balance[item] = script_total_balance[item]
                 
                 
            
    print script_total_balance
            
    with open('Accounts.txt', 'w') as file:
         file.write(json.dumps(account_balance))
    
    '''
    Account.txt - Output
    {"BNB": 0.96284657, "BTC": 0.00191931}     

    '''
    
    return 

bm = BinanceSocketManager(client)
bm.start_user_socket(process_message)
bm.start()