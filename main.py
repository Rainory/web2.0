token = '1477316760:AAFtOgxHQc9PuNBtTvWQ0t4fNJGhXWF4WXk'
#pip install pytelegrambotapi

import telebot

#загружаем токен нашего бота
bot = telebot.TeleBot(token)

def greetings(m):
    text = m.text
    gr = ['привет', 'ку', 'здравствуй', 'хай', 'прив']
    for i in gr:
        if text.find(i) != -1:
            return True
    return False

@bot.message_handler(func=greetings)
def hi_message(m):
    bot.send_message(m.from_user.id, 'Привет, ' + m.from_user.first_name + ')')

bot.polling(none_stop=True, interval=0)