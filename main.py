import telebot #pip install pytelegrambotapi
from telebot import types
import pandas as pd
import numpy as np
import my_parser
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


token = '1477316760:AAFtOgxHQc9PuNBtTvWQ0t4fNJGhXWF4WXk'

#загружаем токен нашего бота
bot = telebot.TeleBot(token)
users = pd.read_csv('users.csv')
packs = pd.read_csv('packs.csv')
current = pd.DataFrame(data=my_parser.get_today(), columns=['name', 'link', 'short_name', 'b_price'])
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
        current = pd.DataFrame(data=my_parser.get_today(), columns=['name', 'link', 'short_name', 'b_price'])
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
    global aut
    if call.data == '/reg':
        #m = bot.send_message(call.from_user.id, 'rere')
        reg(call)
    elif call.data == 'pass':
        cur()
        s = '\n'
        for i in current.values:
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
            if pin == users[users['user_id'] == call.from_user.id]['password'].values:
                bot.send_message(call.from_user.id, 'Вы вошли.\n Для справки введите /help.')
                aut = 1
            else:
                pin = ''
                bot.send_message(call.from_user.id, 'Что-то пошло не так. Введите пинкод заново', reply_markup=form)

@bot.message_handler(commands=['today'])
def today(m):
    global aut
    cur()
    s = 'Рекомендуемые к покупке акции:\n'
    for i in current.values:
        s += f' - ({i[2]}) {i[0]}  текущая стоимость: {i[3]}$\n'
    bot.send_message(m.from_user.id, s)
    if aut == 1:
        bot.send_message(m.from_user.id, '''Можете внести данне о покупке акций. Тогда в будущем можно отследить прибыль.
                                            Для этого вводите строки вида "BIO 4", где в начале стоит короткое наименование акции,
                                            а в конце - количество купленных штук.''')
    else:
        bot.send_message(m.from_user.id, '''Для того, чтобы была возможность отследить прибыль потенциально купленных акций - 
                                            зарегистрируйтесь. Тогда я буду хранить данные о вашем портфеле''')

def buying(x):
    s = x.text.split(' ')
    if s[0] in current['short_name'].values and str.isdigit(s[1]):
        return True
    return False

@bot.message_handler(func=buying)
def buy(m):
    global packs
    s = m.text.split(' ')
    if aut == 0:
        bot.send_message(m.from_user.id, 'Пожалуйста, предворительно зарегистрируйтесь')
        return
    try:
        up = packs[packs['user_id'] == m.from_user.id]
        if s[0] in up['short_name'].values:
            upp = up[up['short_name'] == s[0]]
            am = upp['amount']
            upp['b_price'] = (upp['b_price']*am + current[current['short_name'] == s[0]]['b_price']*int(s[1]))/(am + int(s[1]))
            upp['amount'] = am + int(s[1])
            packs[(packs['user_id'] == m.from_user.id) & (packs['short_name'] == s[0])] = upp
        else:
            d = pd.DataFrame([[m.from_user.id,s[0],
                current[current['short_name'] == s[0]]['link'].values[0],
                int(s[1]),current[current['short_name'] == s[0]]['b_price'].values[0]]],
                columns=['user_id', 'short_name', 'link', 'amount', 'b_price'])
            packs = packs.append(d)
        packs.to_csv('packs.csv', index=False)
        bot.send_message(m.from_user.id, 'Покупка добавлена!')
    except:
        bot.send_message(m.from_user.id, 'Проверьте корректность ввода покупки')

def selling(x):
    s = x.text.split(' ')
    if s[0] == '-' and s[1] in current['short_name'].values and str.isdigit(s[2]):
        return True
    return False

@bot.message_handler(func=selling)
def sell(m):
    global packs
    s = m.text.split(' ')
    if aut == 0:
        bot.send_message(m.from_user.id, 'Пожалуйста, предворительно зарегистрируйтесь')
        return
    try:
        up = packs[packs['user_id'] == m.from_user.id]
        if s[1] in up['short_name'].values:
            upp = up[up['short_name'] == s[1]]
            am = upp['amount'].values[0]
            if am < int(s[2]):
                bot.send_message(m.from_user.id, 'Данных акций не хватает в портфеле')
                return
            upp['b_price'] = (upp['b_price'].values[0]*am - current[current['short_name'] == s[1]]['b_price'].values[0]*int(s[2]))/(am - int(s[2]))
            upp['amount'] = am - int(s[2])
            packs[(packs['user_id'] == m.from_user.id) & (packs['short_name'] == s[1])] = upp
            if upp['amount'].values[0] == 0:
                packs.drop(packs[(packs['user_id'] == m.from_user.id) & (packs['short_name'] == s[1])].index)
                bot.send_message(m.from_user.id, 'Акции проданы и закончились в портфеле')
        else:
            bot.send_message(m.from_user.id, 'Данных акций нет в портфеле!')
        packs.to_csv('packs.csv', index=False)
        bot.send_message(m.from_user.id, 'Акции проданы!')
    except:
        bot.send_message(m.from_user.id, 'Проверьте корректность ввода продажи')

@bot.message_handler(commands=['pack'])
def pack(m):
    #Показывает текущее состояние портфеля
    if aut == 1:
        global packs
        up = packs[packs['user_id'] == m.from_user.id][['short_name', 'amount', 'b_price', 'link']]
        if len(up) == 0:
            bot.send_message(m.from_user.id, 'Ваш портфель пока пуст. Для того, чтобы совершить покупки напишите /today.')
            return
        up['price'] = up['link'].apply(my_parser.price)
        res = sum(up['price'] - up['b_price'])
        s = 'акция количество цена_покупки цена\n\n'
        for i in np.arange(len(up)):
            s += f'{up["short_name"].values[0]}\t{up["amount"].values[0]}\t{up["b_price"].values[0]}\t{up["price"].values[0]}\n'
        s += f'\n Изменение портфеля (прибыль): {res}'
        bot.send_message(m.from_user.id, s + '\n\n Можете также частично продать свои акции, используя "- BIO 5".')
    else:
        bot.send_message(m.from_user.id, 'Пройдите регистрацию, чтобы получить доступ к данной функции. Для этого напишите /reg.')

@bot.message_handler(commands=['reg'])
def reg(m):
    bot.send_message(m.from_user.id, 'Придумайте, пожалуйста, пинкод' + 
                    '(введите 6 цифр):',
                    reply_markup=form)

@bot.message_handler(commands=['help'])
def helper(m):
    bot.send_message(m.from_user.id,
    '''Данный бот будет Вашим помошником в торговле акциями! Имеются такие команды как
    - /reg\tпозволяет зарегистрироваться
    - /today\tпоказывает рекомендуемые акции(доступно без регистрации)
    - /pack\t возвращает текущее состояние вашего портфеля(требуется регистрация)''')

bot.polling(none_stop=True, interval=0)