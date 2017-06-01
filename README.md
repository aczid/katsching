# Katsching

This is meant to monitor a trading bot like [TraderDaddy](https://traderdaddy.com/) in action while operating on the [Bittrex](https://bittrex.com/) exchange.
The script will log the trades and play a 'nomnom' sound for buys and a 'katsching' sound for sales.

You'll need `pygame` and `bittrex` python packages installed.

    pip install -r requirements.txt

Now just fill in your api key and secret into `katsching.py` for a (new) key with 'read info' privileges and run it.

    ./katsching.py

The total balance depicted is the sum of all your btc + the sum of all coins at their current market ask rate.
