import requests
import json


symbol = 'btc'
symbol = symbol.upper()
binance = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT')
print(binance.text)
#{"code":-1100,"msg":"Illegal characters found in parameter 'symbol'; legal range is '^[A-Z0-9-_.]{1,20}$'."}
#{"code":-1121,"msg":"Invalid symbol."}
price = json.loads(binance.text)['price']
rounded_price = str(round(float(price), 2))
print(price)
print(rounded_price)
