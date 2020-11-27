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
    bot.send_message(m.from_user.id, 'Здравствуй, ' + m.from_user.first_name)

@bot.message_handler(commands=['help'])
def helper(m):
    bot.send_message(m.from_user.id,
    '''Данный бот будет Вашим помошником в торговле акциями! Имеются такие команды как
        - /...
    Для подробного описания команды можете добавить к ней "_help". ''')

bot.polling(none_stop=True, interval=0)