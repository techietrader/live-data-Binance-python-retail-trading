"""
Created on Mon June 16 18:03:30 2018

@author: techietrader
"""



from collections import deque
import json
import logging
logging.basicConfig()

'''
Tokens.dat file is for the user to edit the trading pair for which he/she wish to trade or fetch data. 

Tokens.dat - Output
['XRPUSDT','BTCUSDT','NEOUSDT','QTUMUSDT','ETHUSDT','BNBUSDT','ADAUSDT','LTCUSDT','BCCUSDT']

If you want to add new tokens simply add them inside the brackets. 
This is how it should be in the format after adding new token - 'ETHBTC'
['XRPUSDT','BTCUSDT','NEOUSDT','QTUMUSDT','ETHUSDT','BNBUSDT','ADAUSDT','LTCUSDT','BCCUSDT', 'ETHBTC']

'''
 
with open('Tokens.dat','r') as tokens:
    mess=tokens.read()
    instruments=eval(mess) 
 



'''
Lets now figure out for what all pairs we are fetching data for
This list should be the same as Tokens.dat if the pairs contained are all valid.

'''
data_pairs=[]
with open('SymbolValues.csv', 'r') as f:
    q = deque(f, 9000)
    q=map(lambda s: s.strip(), q)
    for i in q[1:]:
        data_pairs.extend([i.split(',')[2]])
data_pairs = list(set(data_pairs))        
# ['ADAUSDT', 'ETHBTC','ETHUSDT', 'NEOUSDT', 'LTCUSDT', 'BNBUSDT', 'BTCUSDT', 'QTUMUSDT', 'BCCUSDT', 'XRPUSDT']

print '{}, these many are Invalid Tokens.'.format([i for i in instruments if i not in data_pairs])
print 'Meanwhile Lets proceed with the valid ones ' 



'''    
Creating a Dictionary object to fetch best bid and ask from SymbolValues.csv to compare it with Scalar values.
Scalar Values could be the values we would want to compare with market prices to take trade decisions on. 
Eg- Moving Average, MACD, etc.  

'''


finalValues={}
for instrument in data_pairs:
    '''
    You can include as may Values [As of now, we have included Best Bid and Best Ask, you can include, CMP, 
    Best Bid Quantity, Best Ask Quantity, etc] for the key. Make sure you also add that many in process_message 
    function in BinanceWSdatacollecter.py. Details as to what many details can we add are available in the 
    docstring of the function.
    '''
    finalValues[instrument]={'bestBid':0.0,'bestAsk':0.0}
    
    
    
'''
Below code looks for last 9000 rows in SymbolValues.csv (you can keep a small figure) to check for the latest 
tick data for the selected number of pairs and than chooses the latest Best Bid and Ask of each pair. 

'''    
while True:
    data=[]
    try:
        with open('SymbolValues.csv', 'r') as f:
            q = deque(f, 9000)
            q=map(lambda s: s.strip(), q)
            for i in q[1:]:
                data.extend([i.split(',')])
    except IOError:
        print 'SymbolValues.csv file is open'
        print 'But Once you close, things will be normal'
        continue
        
    for instrument in finalValues:
        for row in data[1:]:
            if row[2]==instrument:                      
                '''
                Remember to change the column index here should you decide to change the format of 
                SymbolValues.csv inside the process_message function in BinanceWSdatacollecter.py.
                The index is mapped accordingly.
                '''
            
                finalValues[instrument]['bestBid']=float(row[3]) 
                finalValues[instrument]['bestAsk']=float(row[5])


    with open('finalValues.txt', 'w') as file:
        file.write(json.dumps(finalValues))
         
'''
finalValues Format-
{"ADAUSDT": {"bestBid": 0.12895, "bestAsk": 0.129}, "ETHUSDT": {"bestBid": 406.17, "bestAsk": 406.39}, 
"NEOUSDT": {"bestBid": 26.83, "bestAsk": 26.846}, "LTCUSDT": {"bestBid": 73.98, "bestAsk": 74.17}, 
"BNBUSDT": {"bestBid": 13.622, "bestAsk": 13.643}, "BTCUSDT": {"bestBid": 6962.45, "bestAsk": 6964.46}, 
"QTUMUSDT": {"bestBid": 6.43, "bestAsk": 6.44}, "BCCUSDT": {"bestBid": 693.04, "bestAsk": 693.97}} 
       
'''
         
         
         