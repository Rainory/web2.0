import telebot #pip install pytelegrambotapi
from telebot import types
import pandas as pd
import my_parser
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


token = '1477316760:AAFtOgxHQc9PuNBtTvWQ0t4fNJGhXWF4WXk'

#загружаем токен нашего бота
bot = telebot.TeleBot(token)
users = pd.read_csv('users.csv')
current = my_parser.get_today()
time_cur = time.time()
pin = ''
pin_check = ''
n = 0
aut = 0
ind = 0
form = InlineKeyboardMarkup()
for i in range(10):
    form.add(InlineKeyboardButton(text=f'{i}', callback_data=f'{i}'))

def cur():# делает информацию по акциям актуальной
    global current
    global time_cur
    if (time.time() - time_cur)/3600 >= 1:
        current = my_parser.get_today()
        time_cur = time.time()
    return

def greetings(m):
    text = m.text
    gr = ['привет', 'ку', 'здравствуй', 'хай', 'прив']
    for i in gr:
        if text.find(i) != -1:
            return True
    return False

@bot.message_handler(func=greetings)
@bot.message_handler(commands=['start'])
def hi_message(m):
    global n
    bot.send_message(m.from_user.id, 'Здравствуй, ' + m.from_user.first_name)
    if m.from_user.id in list(users['user_id']):
        bot.send_message(m.from_user.id, 'Введите свой пинкод:', reply_markup=form)
        n = 2
    else:
        keyboard = types.InlineKeyboardMarkup()
        k_reg = types.InlineKeyboardButton(text='Зарегистрироваться', callback_data='/reg')
        k_pass = types.InlineKeyboardButton(text='Пропустить', callback_data='pass')
        keyboard.add(k_reg)
        keyboard.add(k_pass)
        bot.send_message(m.from_user.id,
                        'Вижу, что ты еще не регистрировался. Можешь сделать это сейчас или продолжить в режиме просмотра',
                        reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global n
    global pin
    global pin_check
    if call.data == '/reg':
        #m = bot.send_message(call.from_user.id, 'rere')
        reg(call)
    elif call.data == 'pass':
        cur()
        s = '\n'
        for i in current:
            s += f' - ({i[2]}) {i[0]}  текущая стоимость: {i[3]}$\n'
        s += '\nВы все еще можете зарегистрироваться (введите /reg).'
        bot.send_message(call.from_user.id, 'Пусть так. В режиме просмотра вам доступна только данная информация.\n' + s)
    for i in range(10):
        if call.data == str(i) and len(pin) < 6:
            pin += call.data
    if call.from_user.id in users['user_id']:
        if pin == users[users['user_id'] == call.from_user.id]['password']:
            bot.send_message(call.from_user.id, 'Пинкод введен верно!')
            aut = 1
            ind = call.from_user.id
    elif len(pin) == 6:
        if n == 0:
            n = 1
            bot.send_message(call.from_user.id, 'Введите пин еще раз')
            pin_check = pin
            pin = ''
            reg(call)
        elif n == 1:
            if pin == pin_check:
                users.loc[len(users)] = [call.from_user.id, pin]
                users.to_csv('users.csv', index=False)
                bot.send_message(call.from_user.id, 'Пинкод сохранен')
                aut = 1
            else:
                bot.send_message(call.from_user.id, 'Вы ошиблись. Можете начать регистрацию заново, написав /reg')
                pin = ''
                pin_check = ''
        else:
            print(users[users['user_id'] == call.from_user.id]['password'].values)
            if pin == users[users['user_id'] == call.from_user.id]['password'].values:
                bot.send_message(call.from_user.id, 'Вы вошли.\n Для справки введите /help.')
                aut = 1
            else:
                pin = ''
                bot.send_message(call.from_user.id, 'Что-то пошло не так. Введите пинкод заново', reply_markup=form)

@bot.message_handler(commands=['reg'])
def reg(m):
    form = InlineKeyboardMarkup()
    bot.send_message(m.from_user.id, 'Придумайте, пожалуйста, пинкод' + 
                    '(введите 6 цифр):',
                    reply_markup=form)

@bot.message_handler(commands=['help'])
def helper(m):
    bot.send_message(m.from_user.id,
    '''Данный бот будет Вашим помошником в торговле акциями! Имеются такие команды как
        - /reg позволяет зарегистрироваться
        - /...
    Для подробного описания команды можете добавить к ней "_help". ''')

bot.polling(none_stop=True, interval=0)