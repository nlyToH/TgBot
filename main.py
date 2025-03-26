import os
import requests
import telebot
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YANDEX_WEATHER_API_KEY = os.getenv("YANDEX_WEATHER_API_KEY")
LATTITUDE = os.getenv("LATTITUDE")
LONGTITUDE = os.getenv("LONGTITUDE")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def get_weather():
    url = "https://api.weather.yandex.ru/v2/forecast"
    headers = {"X-Yandex-API-Key": YANDEX_WEATHER_API_KEY}
    params = {
        "lat": LATTITUDE,
        "lon": LONGTITUDE,
        "extra": "true",
        "limit": 3
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    rain_days = set()
    today = datetime.utcnow().date()

    for forecast in data.get("forecasts", []):
        date = datetime.strptime(forecast["date"], "%Y-%m-%d").date()
        if date in {today - timedelta(days=1), today, today + timedelta(days=1)}:
            if any(part["prec_mm"] > 0 for part in forecast["parts"].values() if "prec_mm" in part):
                rain_days.add(date)

    return not bool(rain_days)


@bot.message_handler(commands=['rain'])
def rain_command(message):
    try:
        is_dry = get_weather()
        bot.reply_to(message, str(is_dry))
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")


bot.polling(none_stop=True)


