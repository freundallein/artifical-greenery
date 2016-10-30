from AGControl import *

import telebot

TOKEN = 'your token'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/status', '/autocontrol')
    markup.row('/light', '/fan')
    help_msg = 'Commands: /status - for checking AG status,\n /light - for switchinf lights,\n /fan - for switching fan,\n /autocontrol - for setting autocontrol ON'
    bot.send_message(message.chat.id, help_msg, reply_markup=markup)


@bot.message_handler(commands=['status'])
def tb_status(message):
    bot.send_message(message.chat.id, get_status())


@bot.message_handler(commands=['light'])
def tb_switchlight(message):
    manual_switch('light')
    bot.send_message(message.chat.id, 'Lights switched, Autocontrol turned OFF')
    bot.send_message(message.chat.id, get_status())


@bot.message_handler(commands=['fan'])
def tb_switchfan(message):
    manual_switch('fan')
    bot.send_message(message.chat.id, 'Fan switched, Autocontrol turned OFF')
    bot.send_message(message.chat.id, get_status())


@bot.message_handler(commands=['autocontrol'])
def tb_switchfan(message):
    controls.set_autocontrol_flag(True)
    bot.reply_to(message, "Autocontrol turned ON")
    bot.send_message(message.chat.id, get_status())


def ag_telebot():
    while controls.get_working_flag():
        bot.polling(none_stop=True, interval=2)

