import os
import logging
import pandas as pd
import ccxt
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import time

print("🚀 BTC Signal Bot запускается...")

# ============================
# НАСТРОЙКИ
# ============================
SYMBOL = 'BTC/USDT:USDT'
TIMEFRAME_MAIN = '15m'
INTERVAL_CHECK = 900
TELEGRAM_BOT_TOKEN = "ваш_токен"      # ⬅️ ЗАМЕНИТЕ
TELEGRAM_CHAT_ID = "ваш_chat_id"      # ⬅️ ЗАМЕНИТЕ

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

exchange = ccxt.bybit({'enableRateLimit': True})
last_signal = None

def calculate_signal(df):
    """Простая логика для теста"""
    current_price = df['close'].iloc[-1]
    prev_price = df['close'].iloc[-2]
    
    if current_price > prev_price:
        return "LONG"
    elif current_price < prev_price:
        return "SHORT"
    return None

async def check_and_signal():
    global last_signal
    
    try:
        logger.info("🔍 Проверяем рынок...")
        ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME_MAIN, limit=10)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        signal = calculate_signal(df)
        current_price = df['close'].iloc[-1]
        
        if signal and signal != last_signal:
            await send_telegram_alert(signal, current_price)
            last_signal = signal
            logger.info(f"✅ Отправлен сигнал: {signal}")
        else:
            logger.info(f"📊 Цена: ${current_price:.2f}, Сигнал: {signal}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

async def send_telegram_alert(signal, price):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        message = f"""
🎯 BTC SIGNAL

📈 Направление: {signal}
💰 Цена: ${price:.2f}
⏰ Время: {datetime.now().strftime('%d.%m %H:%M')}

⚡ Bybit Futures | 10x Leverage
        """
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"❌ Ошибка Telegram: {e}")

async def main():
    logger.info("🚀 Бот запущен на Render!")
    while True:
        await check_and_signal()
        await asyncio.sleep(INTERVAL_CHECK)

if __name__ == "__main__":
    asyncio.run(main())