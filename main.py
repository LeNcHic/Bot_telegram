import src.flat_parser as flat_parser
import src.config as config
import telebot
import sqlite3


flag_in_system = False
data_base = []
deal_type = ''
accommodation_type = ''
location = ''
rooms = 0
data_frame = None

conn = sqlite3.connect('data/users_bot.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   username TEXT,
                   password TEXT)''')
conn.commit()

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_handler(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    login_button = telebot.types.KeyboardButton('Вход')
    register_button = telebot.types.KeyboardButton('Регистрация')
    keyboard.add(login_button, register_button)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Вход')
def login_handler(message):
    bot.send_message(message.chat.id, 'Введите логин:')
    bot.register_next_step_handler(message, login_password_handler)


def login_password_handler(message):
    username = message.text
    bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(message, lambda m: check_login_password(m, username))


def check_login_password(message, username):
    global flag_in_system
    password = message.text
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    if user:
        bot.send_message(message.chat.id, 'Вы успешно вошли!')
        flag_in_system = True
    else:
        bot.send_message(message.chat.id, 'Неверный логин или пароль.')


@bot.message_handler(func=lambda message: message.text == 'Регистрация')
def register_handler(message):
    bot.send_message(message.chat.id, 'Введите имя:')
    bot.register_next_step_handler(message, username_handler)


def username_handler(message):
    name = message.text
    bot.send_message(message.chat.id, 'Введите логин:')
    bot.register_next_step_handler(message, lambda m: check_username(m, name))


def check_username(message, name):
    username = message.text
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    if user:
        bot.send_message(message.chat.id, 'Этот логин уже занят.')
        return
    bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(message, lambda m: save_user(m, name, username))


def save_user(message, name, username):
    password = message.text
    cursor.execute('INSERT INTO users (name, username, password) VALUES (?, ?, ?)', (name, username, password))
    conn.commit()
    bot.send_message(message.chat.id, 'Вы успешно зарегистрировались!')


@bot.message_handler(commands=['search'])
def start_handler(message):
    global flag_in_system
    if not flag_in_system:
        bot.send_message(message.chat.id, 'Войдите в систему!')
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        rent_button = telebot.types.KeyboardButton('rent')
        sale_button = telebot.types.KeyboardButton('sale')
        keyboard.add(rent_button, sale_button)
        msg = bot.send_message(message.chat.id, 'Выберите тип аренды/покупки:', reply_markup=keyboard)
        bot.register_next_step_handler(msg, apartment_handler)


@bot.message_handler(func=lambda message: message.text == 'rent' or message.text == 'sale')
def apartment_handler(message):
    global deal_type
    deal_type = message.text
    if deal_type == 'rent':
        deal_type += '_long'
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    flat_button = telebot.types.KeyboardButton('flat')
    room_button = telebot.types.KeyboardButton('room')
    house_button = telebot.types.KeyboardButton('house')
    house_part_button = telebot.types.KeyboardButton('house-part')
    townhouse_button = telebot.types.KeyboardButton('townhouse')
    keyboard.add(flat_button, room_button, house_button, house_part_button, townhouse_button)
    msg = bot.send_message(message.chat.id, 'Выберите тип недвижимости:', reply_markup=keyboard)
    bot.register_next_step_handler(msg, city_handler)


@bot.message_handler(func=lambda message: message.text in ['flat', 'room', 'house', 'house-part', 'townhouse'])
def city_handler(message):
    global accommodation_type
    accommodation_type = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    moscow_button = telebot.types.KeyboardButton('Москва')
    peter_button = telebot.types.KeyboardButton('Санкт-Петербург')
    kazan_button = telebot.types.KeyboardButton('Казань')
    nij_novgorod_button = telebot.types.KeyboardButton('Нижний Новгород')
    krasnadar_button = telebot.types.KeyboardButton('Краснодар')
    keyboard.add(moscow_button, peter_button, kazan_button, nij_novgorod_button, krasnadar_button)
    msg = bot.send_message(message.chat.id, 'Выберите город из топ 5 или введите свой вариант:', reply_markup=keyboard)
    bot.register_next_step_handler(msg, room_handler)


@bot.message_handler(func=lambda message: not message.text.isdigit())
def room_handler(message):
    global location
    location = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    one_room_button = telebot.types.KeyboardButton('1')
    two_room_button = telebot.types.KeyboardButton('2')
    three_room_button = telebot.types.KeyboardButton('3')
    four_room_novgorod_button = telebot.types.KeyboardButton('4')
    five_room_button = telebot.types.KeyboardButton('5')
    keyboard.add(one_room_button, two_room_button, three_room_button, four_room_novgorod_button, five_room_button)
    msg = bot.send_message(message.chat.id, 'Выберите кол-во комнат или введите свой вариант:', reply_markup=keyboard)
    bot.register_next_step_handler(msg, search_handler)


@bot.message_handler(func=lambda message: message.text.isdigit())
def search_handler(message):
    global rooms
    global accommodation_type
    global deal_type
    global location
    global data_frame
    rooms = int(message.text)
    data_frame = flat_parser.get_data(deal_type, accommodation_type, location, rooms)
    arr_links = flat_parser.get_top_links(data_frame)
    for i in range(5):
        bot.send_message(message.chat.id, arr_links[i])


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id,
                     '''
                     <em>/start</em> - start searching
                     <em>/help</em> - general tools
                     '''
                     , parse_mode='html')


bot.polling(none_stop=True)
