import telebot
import wikipedia
import requests
from bs4 import BeautifulSoup
from pyowm.owm import OWM
from key import API_KEY, OWM_KEY


# documentation for telebot
# https://github.com/eternnoir/pyTelegramBotAPI/blob/master/README.md#methods

bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['greet'])
def greet(message):
    bot.reply_to(message, "Hey, how r u, dear?")


# handles all text messages that contains /hello
@bot.message_handler(commands=['hello'])
def hello(message):
    bot.send_message(message.chat.id, "Hello, my friend! <3")
    photo = open('picture.jpg', 'rb')
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Okaaay, lets start!\n\n"
                                      "/hello - to get pretty pic\n"
                                      "/time - to get time\n"
                                      "/weather - to get weather from OpenWeatherMap\n"
                                      "/news - to get latest news from RIA Novosti\n"
                                      "and if u just type some word, i send u a lil bit "
                                      "info about it from wiki\n")


@bot.message_handler(commands=['time'])
def handle_time(message):
    sent = bot.send_message(message.chat.id, "entry city or country...")
    bot.register_next_step_handler(sent, get_time)


def get_time(message):
    try:
        place = message.text
        page = requests.get('https://www.google.com/search?q=time+in+' + place)
        soup = BeautifulSoup(page.text, "lxml")
        time = soup.find_all(class_="BNeawe iBp4i AP7Wnd")[1].text
        bot.send_message(message.chat.id, 'time in {}:  {}'.format(place, time))
    except:
        bot.send_message(message.chat.id, "there is no such place, check all letters, lovely")


@bot.message_handler(commands=['weather'])
def handle_weather(message):
    sent = bot.send_message(message.chat.id, "entry city or country...")
    bot.register_next_step_handler(sent, get_weather)


def get_weather(message):
    try:
        place = message.text
        owm = OWM(OWM_KEY)
        mgr = owm.weather_manager()
        # The weather object holds all weather-related info
        weather = mgr.weather_at_place(place).weather

        temp = weather.temperature('celsius')  # a dict in Celsius units
        t_min = int(temp['temp_min'])
        t_max = int(temp['temp_max'])
        status = weather.detailed_status  # eg. 'light rain'
        wind = weather.wind()['speed']  # Default unit: 'meters_sec'

        res = 'weather in {}:\n{},\ntemp  {}-{} °C,\nwind  {} m/s'.format(place, status, t_min, t_max, wind)
        bot.send_message(message.chat.id, res)
    except:
        bot.send_message(message.chat.id, "there is no such place, check all letters, lovely")


@bot.message_handler(commands=['news'])
def handle_news(message):
    bot.send_message(message.chat.id, get_news())


# returns 10 latest news
def get_news():
    page = requests.get('https://ria.ru/')
    soup = BeautifulSoup(page.text, "lxml")
    news = soup.find_all(class_="cell-list__item-link color-font-hover-only")[:10]
    s = ''
    for a in news:
        # print(a.attrs)
        s += a['title'] + '\n' + a['href'] + '\n\n'
    return s


wikipedia.set_lang('ru')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_message(message.chat.id, get_wiki(message.text))


def get_wiki(s):
    try:
        raw_text = wikipedia.page(s).content[:1000]  # get 1000 symbols from wiki page
        sentences = raw_text.split('.')[:-1]   # leave only the text up to the last point

        # leave only sentences with more than three characters
        # sentences like "См." will be discarded
        text = '.'.join(sentence for sentence in sentences if len(sentence) > 3) + '.'
        return text
    except:
        return 'I dont know this word'


# upon calling this function, TeleBot starts polling the Telegram servers for new messages
bot.polling()