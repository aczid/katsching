#!/usr/bin/python2.7

import time
from bittrex import *

def timestamp(s):
    from dateutil.parser import parse
    return parse(s['TimeStamp']).strftime("%Y-%m-%d %H:%M:%S:%f")

def play_sound(sound):
    from pygame import mixer
    mixer.init()
    mixer.music.load(sound)
    mixer.music.play()
    time.sleep(1)
    mixer.quit()

b = Bittrex('API_KEY', 'API_SECRET')
sales = []
buys = []
closed_orders = b.api_query('getorderhistory')
for order in closed_orders['result']:
    if order['OrderType'] == 'LIMIT_SELL':
        sales.append(order)
    if order['OrderType'] == 'LIMIT_BUY':
        buys.append(order)
play_sound('katsching.wav')

while True:
    try:
        new_sales = []
        new_buys = []
        closed_orders = b.api_query('getorderhistory')['result']
        for order in closed_orders:
            if order['OrderType'] == 'LIMIT_SELL':
                if order not in sales:
                    new_sales.append(order)
            if order['OrderType'] == 'LIMIT_BUY':
                if order not in buys:
                    new_buys.append(order)

        if len(new_buys) or len(new_sales):
            # Get total balance
            total = 0
            summaries = b.get_market_summaries()['result']
            balances = b.get_balances()['result']
            for bal in balances:
                if bal['Currency'] != 'BTC':
                    total += bal['Balance'] * filter(lambda x: x['MarketName'] == 'BTC-'+bal['Currency'], summaries)[0]['Ask']
                else:
                    total += bal['Balance']

            # Count open buy / sell orders
            open_orders = b.api_query('getopenorders')['result']
            open_buys = {}
            open_sales = {}
            for order in open_orders:
                if order['Exchange'] not in open_buys.keys():
                    open_buys[order['Exchange']] = {'total_coin': 0, 'total_btc': 0, 'average_price': 0.0, 'count': 0}
                if order['Exchange'] not in open_sales.keys():
                    open_sales[order['Exchange']] = {'total_coin': 0, 'total_btc': 0, 'average_price': 0.0, 'count': 0}
                if order['OrderType'] == 'LIMIT_SELL':
                    open_sales[order['Exchange']]['total_btc']  += order['Limit']*order['Quantity']
                    open_sales[order['Exchange']]['total_coin'] += order['Quantity']
                    open_sales[order['Exchange']]['count'] += 1
                if order['OrderType'] == 'LIMIT_BUY':
                    open_buys[order['Exchange']]['total_btc']  += order['Limit']*order['Quantity']
                    open_buys[order['Exchange']]['total_coin'] += order['Quantity']
                    open_buys[order['Exchange']]['count'] += 1

            # Compute average buy/sell prices
            for x in open_sales:
                if open_sales[x]['total_coin']:
                    open_sales[x]['average_price'] = open_sales[x]['total_btc']/open_sales[x]['total_coin']
            for x in open_buys:
                if open_buys[x]['total_coin']:
                    open_buys[x]['average_price'] = open_buys[x]['total_btc']/open_buys[x]['total_coin']

            # Alert activity
            if len(new_sales):
                play_sound('katsching.wav')
            if len(new_buys):
                play_sound('nomnom.wav')

            # Log new trades
            for order in new_sales:
                avg_price = open_sales[order['Exchange']]['average_price']
                open_buy_count = open_buys[order['Exchange']]['count']
                open_sale_count = open_sales[order['Exchange']]['count']
                coin_name = order['Exchange'].replace('BTC-', '').rjust(5)
                print ' '.join([
                        timestamp(order),
                        "Sold  ", ("%0.08f" % order['Quantity']).rjust(12), coin_name, '@', "%0.08f" % order['PricePerUnit'],
                        "| avg sell limit @ %0.8f" % avg_price,
                        "| %02d/%02d" % (open_buy_count, open_sale_count), coin_name, "buy/sell orders",
                        "| total @ %0.12f BTC" % total,
                        ])
                sales.append(order)
            for order in new_buys:
                avg_price = open_buys[order['Exchange']]['average_price']
                open_buy_count = open_buys[order['Exchange']]['count']
                open_sale_count = open_sales[order['Exchange']]['count']
                coin_name = order['Exchange'].replace('BTC-', '').rjust(5)
                print ' '.join([
                        timestamp(order),
                        "Bought", ("%0.08f" % order['Quantity']).rjust(12), coin_name, '@', "%0.08f" % order['PricePerUnit'],
                        "| avg buy  limit @ %0.8f" % avg_price,
                        "| %02d/%02d" % (open_buy_count, open_sale_count), coin_name, "buy/sell orders",
                        "| total @ %0.12f BTC" % total,
                        ])
                buys.append(order)
    except Exception, e:
        print e
    time.sleep(10)

