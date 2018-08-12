
## Welcome to this project

Python Scripts to fetch live streaming cryptocurrency pricing data from Binance.com
 
## Getting Started

I have built the system from retail trading point of view without using OOPS programming. 
This is also to demonstrate the power of Python functional programming and may be a starting point for retail traders to get into Algo trading space in crypto trading.

### Prerequisites
Python Functional Programming knowledge. 

API_keys of your Binance Account (Binance.com)

Python 2 (https://www.anaconda.com/download/)

Python-Binance API (https://github.com/sammchardy/python-binance)


### Note

Pandas_verion -> 0.20.3


### Installing and Running

Download files into a folder and using 3 instances of terminal/git bash or Command Prompt window to run the .py files one by one in each instance.


### Steps Involved

1.	Jot down your api and the secret as shown in the image below
2.	Open the Tokens.dat file and put in the trading pairs you either wish to trade or wants to keep a watch on. Keep on adding tokens one after another in the list. Here is the image –
3.	SymbolValues.csv, finalValues.txt, Orders.csv, Accounts.txt. These four files are the parameters/output of running the scripts.
	1.	SymbolValues.csv is generated while running BinanceWSdatacollecter.py. 
	2.	finalValues.txt contains the Best Bid price and the Best ask price of a particular token/ pair which is updated everytime a new data point comes in. This file is generated and gets appended in Market_data_parser.py
	3.	Orders.csv and Accounts.txt records your number of orders executed and the balance details using the secret api key which happens in the script Orders_Accounts.py

 
### About the three scripts

1.	BinanceWSdatacollecter.py collects the data for the trading spread that is specified in the Tokens.dat file. You can decide the format of the data required inside the process_message function. A very details docstring provided inside the function. The data that is collected can be used for trading and further analysis
2.	Market_data_parse.py kind of does the same thing but provide data in a more compact format. For example, currently we have chosen to take only the BestBid and BestAsk values of every pair we have chosen. This data can be utilized to take trading decision, something like- 
```
If BestBid > MA21:
	Call Buy_trade_api
Else:
	Vice versa
```
3.	Orders_Accounts.py does the best at recording trades in the Orders.csv and updates the Accounts file with the balances.
Binance has put a few constraints on the value of the trade order and the minimum quantity to be ordered. This script takes care of those constraints and filters out the tokens which does not meet the constrain requirements. More details inside the file.


### What Next

Try creating a trading algorithm that takes input from finalValues.txt, Orders.csv and Accounts.txt and outputs a trade.




##### Disclaimer – I’m not associated with Binance. Use at your own risk.
