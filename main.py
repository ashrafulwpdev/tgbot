import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Telegram Bot Token
TOKEN = '6787730433:AAHFGxq9NB7ibH0uw91P2o_Jguo9t7keAIo'

# CoinGecko API URL
CRYPTO_API_URL = 'https://api.coingecko.com/api/v3'

# CoinMarketCap API URL and API Key
COINMARKETCAP_API_URL = 'https://pro-api.coinmarketcap.com/v1'
COINMARKETCAP_API_KEY = '1f3c28d5-97e7-4aa3-b765-d4e9ed661e14'

# Admin Telegram User IDs
admins = '12345678'

# Initialize a dictionary to store user wallets
user_wallets = {}

def get_crypto_price_coin_gecko(symbol):
    url = f"{CRYPTO_API_URL}/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    if symbol in data:
        return data[symbol]['usd']
    else:
        return None

def get_crypto_details_coin_gecko(symbol):
    url = f"{CRYPTO_API_URL}/coins/markets?vs_currency=usd&ids={symbol}"
    response = requests.get(url)
    data = response.json()
    if data:
        details = data[0]
        return {
            'current_price': details['current_price'],
            'high_24h': details['high_24h'],
            'low_24h': details['low_24h'],
            'price_change_percentage_7d': details['price_change_percentage_7d_in_currency'],
            'total_volume': details['total_volume'],
            'market_cap': details['market_cap']
        }
    else:
        return None

def get_crypto_details_coin_market_cap(symbol):
    url = f"{COINMARKETCAP_API_URL}/cryptocurrency/quotes/latest"
    params = {
        'symbol': symbol,
        'convert': 'USD'
    }
    headers = {
        'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if 'data' in data and symbol.upper() in data['data']:
        details = data['data'][symbol.upper()]['quote']['USD']
        return {
            'current_price': details['price'],
            'high_24h': details['high_24h'],
            'low_24h': details['low_24h'],
            'price_change_percentage_7d': details['percent_change_7d'],
            'total_volume': details['volume_24h'],
            'market_cap': details['market_cap']
        }
    else:
        return None

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! I\'m a cryptocurrency price tracker bot.')

def price(update: Update, context: CallbackContext) -> None:
    parts = context.args
    if len(parts) == 1:
        symbol = parts[0].upper()
        details = get_crypto_details_coin_gecko(symbol)
        if not details:
            details = get_crypto_details_coin_market_cap(symbol)
        if details:
            update.message.reply_text(
                f"The current price of {symbol} is ${details['current_price']}\n"
                f"24h High: ${details['high_24h']}\n"
                f"24h Low: ${details['low_24h']}\n"
                f"7-day Change: {details['price_change_percentage_7d']}%\n"
                f"Volume: ${details['total_volume']}\n"
                f"Market Cap: ${details['market_cap']}"
            )
        else:
            update.message.reply_text(f"Sorry, could not retrieve details for {symbol}")
    else:
        update.message.reply_text("Invalid command. Usage: /price <crypto_symbol>")

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Handlers
    start_handler = CommandHandler("start", start)
    price_handler = CommandHandler("price", price)

    # Add handlers to dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(price_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
