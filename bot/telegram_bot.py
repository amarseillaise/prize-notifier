import telebot
import os


from init_service import init_env_vars
from bot.service_bot import DobryPizeBotService

init_env_vars('bot.env')
current_thread = ...
bot_service = DobryPizeBotService()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def start(message):
    bot_service.start(message.chat)

@bot.message_handler(commands=['stop'])
def stop(message):
    bot_service.stop(message.chat)

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    bot_service.subscribe(bot, message)

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    bot_service.unsubscribe(bot, message)

@bot.message_handler(commands=['list_prize'])
def list_prize(message):
    bot_service.send_prizes_list(bot, message)

@bot.message_handler(commands=['wishlist'])
def wishlist(message):
    bot_service.send_wishlist(bot, message)

@bot.message_handler(commands=['add_to_wishlist'])
def add_to_wishlist(message):
    bot_service.add_prize_to_wishlist(bot, message)

@bot.message_handler(commands=['remove_from_wishlist'])
def remove_from_wishlist(message):
    bot_service.remove_prize_from_wishlist(bot, message)

def main():
    bot_service.init_commands(bot)
    if bot_service.check_start_site_polling():
        bot_service.start_prizes_polling(bot)
    bot.infinity_polling()

if __name__ == "__main__":
    main()

