import telebot
from AGControl import *
from DBMaintenance import db_reading
from mail import mail_send

#from package.mail import *

bot = telebot.TeleBot(config.TOKEN)

approved_ids = config.approved_users

deny_msg = "Denied. Your ID isn't approved by administrator."

@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/status', '/autocontrol')
    markup.row('/light', '/fan')
    markup.row('/report')
    help_msg = '''Commands: \n/status - for checking AG status,\n
                /light - for switching lights,\n
                /fan - for switching fan,\n
                /autocontrol - for setting autocontrol ON,\n
                /report - mails daily report to administrator.'''
    bot.send_message(message.chat.id, help_msg, reply_markup=markup)


@bot.message_handler(commands=['status'])
def tb_status(message):
    bot.send_message(message.chat.id, get_status())


@bot.message_handler(commands=['light'])
def tb_switchlight(message):
    if message.from_user.id in approved_ids:
        manual_switch('light')
        bot.send_message(message.chat.id, 'Lights switched, Autocontrol turned OFF')
        bot.send_message(message.chat.id, get_status())
    else:
        bot.send_message(message.chat.id, deny_msg)
        bot.send_message(config.administrator_id, str(message.from_user.id) + " trying to access.")


@bot.message_handler(commands=['fan'])
def tb_switchfan(message):
    if message.from_user.id in approved_ids:
        manual_switch('fan')
        bot.send_message(message.chat.id, 'Fan switched, Autocontrol turned OFF')
        bot.send_message(message.chat.id, get_status())
    else:
        bot.send_message(message.chat.id, deny_msg)
        bot.send_message(config.administrator_id, str(message.from_user.id) + " trying to access.")


@bot.message_handler(commands=['autocontrol'])
def tb_switchfan(message):
    if message.from_user.id in approved_ids:
        controls.set_autocontrol_flag(True)
        bot.reply_to(message, "Autocontrol turned ON")
        bot.send_message(message.chat.id, get_status())
    else:
        bot.send_message(message.chat.id, deny_msg)
        bot.send_message(config.administrator_id, str(message.from_user.id) + " trying to access.")


@bot.message_handler(commands=['report'])
def tb_status(message):
    if message.from_user.id in approved_ids:
        mail_send(db_reading())
        bot.send_message(message.chat.id, "Daily report sent.")
    else:
        bot.send_message(message.chat.id, deny_msg)
        bot.send_message(config.administrator_id, str(message.from_user.id) + " trying to access.")


def ag_telebot():
    while controls.get_working_flag():
        bot.polling(none_stop=True, interval=2)
