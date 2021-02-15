"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from config.rxConfig import telegram as telegram_config
telegramToken = telegram_config['telegram-token']
botUpdatesChannel = telegram_config['botupdates']
import core
import logging
from telegram import Update, Bot, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

debug = False

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
bot = Bot(telegramToken)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Please only send single messages.')

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if debug:
        ai_response = core.chat(str(update.message.text), str(update.message.from_user.id))
    else:
        try:
            ai_response = core.chat(str(update.message.text), str(update.message.from_user.id))
        except Exception as e:
            print(e)
            updateMessage = 'ERROR: ' + str(e)
            bot.send_message(botUpdatesChannel, text=updateMessage)
            ai_response = 'An error occured. Please try again later.'
            if str(update.message.from_user.id) in core.sudoers:
                ai_response = ai_response + '\n' + str(e)
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    update.message.reply_text(str(ai_response))

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegramToken, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    print('Ready.')
    bot.send_message(botUpdatesChannel, text="Online.")
    updater.idle()


if __name__ == '__main__':
    core.init()
    main()
