import telebot
import sys
from AGControl import *
from DBMaintenance import db_reading
from mail import mail_send


bot = telebot.TeleBot(config.TOKEN)


def deny_send(message):
    deny_msg = "Denied. Your ID isn't approved by administrator."
    bot.send_message(message.chat.id, deny_msg)
    bot.send_message(config.administrator_id, str(message.from_user.id) + " trying to access.")


@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/status', '/autocontrol')
    markup.row('/light', '/fan')
    markup.row('/report', '/shutdown')
    help_msg = '''Commands: \n/status - for checking AG status,\n
                /light - for switching lights,\n
                /fan - for switching fan,\n
                /autocontrol - for setting autocontrol ON,\n
                /report - mails daily report to administrator,\n
                /shutdown - for shutdown greenery.'''
    bot.send_message(message.chat.id, help_msg, reply_markup=markup)


@bot.message_handler(commands=['status'])
def tb_status(message):
    bot.send_message(message.chat.id, get_status())


@bot.message_handler(commands=['light'])
def tb_switchlight(message):
    if message.from_user.id in config.approved_users:
        manual_switch('light')
        bot.send_message(message.chat.id, 'Lights switched, Autocontrol turned OFF')
        bot.send_message(message.chat.id, get_status())
    else:
        deny_send(message)


@bot.message_handler(commands=['fan'])
def tb_switchfan(message):
    if message.from_user.id in config.approved_users:
        manual_switch('fan')
        bot.send_message(message.chat.id, 'Fan switched, Autocontrol turned OFF')
        bot.send_message(message.chat.id, get_status())
    else:
        deny_send(message)


@bot.message_handler(commands=['autocontrol'])
def tb_switchfan(message):
    if message.from_user.id in config.approved_users:
        controls.set_autocontrol_flag(True)
        bot.reply_to(message, "Autocontrol turned ON")
        bot.send_message(message.chat.id, get_status())
    else:
        deny_send(message)


@bot.message_handler(commands=['report'])
def tb_status(message):
    if message.from_user.id in config.approved_users:
        mail_send(db_reading())
        bot.send_message(message.chat.id, "Daily report sent.")
    else:
        deny_send(message)


@bot.message_handler(commands=['shutdown'])
def shutdown_by_tb(message):
    if message.from_user.id in config.approved_users:
        bot.send_message(message.chat.id, "AG shutdown executed.")
        GPIO.cleanup()
        sys.exit()
    else:
        deny_send(message)


@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id == config.administrator_id:
        try:
            id_to_add = int(telebot.util.extract_arguments(message.text))
            config.approved_users.append(id_to_add)
            bot.send_message(message.chat.id, "approved.")
        except ValueError:
            bot.send_message(message.chat.id, "ID must be integer.")
    else:
        deny_send(message)


@bot.message_handler(commands=['delete'])
def delete_user(message):
    if message.from_user.id == config.administrator_id:
        try:
            id_to_delete = int(telebot.util.extract_arguments(message.text))
            config.approved_users.remove(id_to_delete)
            bot.send_message(message.chat.id, "deleted.")
        except ValueError:
            bot.send_message(message.chat.id, "ID must be integer.")
    else:
        deny_send(message)


def ag_telebot():
    while controls.get_working_flag():
        bot.polling(none_stop=True, interval=2)
