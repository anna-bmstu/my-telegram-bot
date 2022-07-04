import telebot
import wikipedia
import re
import requests
from bs4 import BeautifulSoup
from key import API_KEY

# documentation for telebot
# https://github.com/eternnoir/pyTelegramBotAPI/blob/master/README.md#methods

bot = telebot.TeleBot(API_KEY)

# message.content_type (for example 'text', 'document', 'audio')
# message.text (smth that user wrote to bot)


@bot.message_handler(commands=['greet'])
def greet(message):
    bot.reply_to(message, "Hey, how r u, dear?")


# handles all text messages that contains /hello
@bot.message_handler(commands=['hello'])
def hello(message):
    bot.send_message(message.chat.id, "Hello, my friend! <3")
    photo = open('picture.jpg', 'rb')      # my bot can send pretty pic
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Okaaay, lets start!\nI can do a lot of things. "
                                      "Ur virtual friend is very clever :)\n"
                                      "1. if u just type some word, i send u a lil bit "
                                      "info about it pulled from wiki\n")


@bot.message_handler(commands=['time'])
def handle_time(message):
    sent = bot.send_message(message.chat.id, "entry city or country...")
    bot.register_next_step_handler(sent, get_time)


def get_time(message):
    try:
        place = message.text
        page = requests.get('https://www.google.com/search?client=firefox-b-d&q=time+in+' + place)
        soup = BeautifulSoup(page.text, "lxml")
        time = soup.find_all(class_="BNeawe iBp4i AP7Wnd")[1].text
        bot.send_message(message.chat.id, 'time in {}:  {}'.format(place, time))
    except:
        bot.send_message(message.chat.id, "there is no such place in the whole world, check all letters, lovely")


wikipedia.set_lang('ru')


def get_wiki(s):
    try:
        raw_text = wikipedia.page(s).content[:1000]  # get 1000 symbols from wiki page
        sentences = raw_text.split('.')[:-1]   # leave only the text up to the last point

        # leave only sentences with more than three characters
        # sentences like "См." will be discarded
        text = '.'.join(sentence for sentence in sentences if len(sentence) > 3) + '.'
        return text
    except:
        return 'wiki has no info about it :( check ur spelling, dear'


@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_message(message.chat.id, get_wiki(message.text))





# upon calling this function, TeleBot starts polling the Telegram servers for new messages
bot.polling()
