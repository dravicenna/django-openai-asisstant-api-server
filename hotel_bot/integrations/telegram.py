"""
Setting Up Telegram Integration

To integrate a Telegram bot into your application, you'll need to first create the bot on Telegram and then configure your environment (like Replit) to use it. Here's a step-by-step guide:

1. Create a Telegram Bot:
   - Start by searching for 'BotFather' on Telegram. This is an official bot that Telegram uses to create and manage other bots.
   - Send the '/newbot' command to BotFather. It will guide you through creating your bot. You'll need to choose a name and a username for your bot.
   - Upon successful creation, BotFather will provide you with an API token. This token is essential for your bot's connection to the Telegram API.

2. Add the API Key to Replit:
   - Go to your Replit project where you intend to use the Telegram bot.
   - Open the 'Secrets' tab (usually represented by a lock icon).
   - Create a new secret with the key as `TELEGRAM_TOKEN` and the value as the API token provided by BotFather.
"""
import json
import logging

from celery import shared_task
from django.http import JsonResponse
from django.views import View
from telebot import TeleBot
from telebot.types import Update

from api.models import TelegramUser, Thread
from assistant.settings import TELEGRAM_TOKEN
from hotel_bot.assistant import assistant

# Configure logging
logging.basicConfig(level=logging.INFO)


bot: TeleBot = TeleBot(TELEGRAM_TOKEN, threaded=False, skip_pending=True)

if not TELEGRAM_TOKEN:
    raise ValueError('No Telegram token found in environment variables')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    u = TelegramUser.get_user(message)
    logging.info(f'Starting a new conversation... {message.chat.id}')
    if not u.thread:
        thread = assistant.client.beta.threads.create()
        u.thread = Thread.objects.create(thread_id=thread.id)
        u.save()
        logging.info(f'New thread created with ID: {thread.id}')
    bot.reply_to(message, "Hello, I'm Virtual Assistant of Hotel. How can I help you?")


@bot.message_handler(commands=['cancel'])
def cancel(message):
    u = TelegramUser.get_user(message)
    if not u.thread:
        return
    thread = assistant.client.beta.threads.create()
    u.thread = Thread.objects.create(thread_id=thread.id)
    u.save()
    bot.reply_to(message, 'Thread reseted')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        u = TelegramUser.get_user(message)
        chat_id = message.chat.id
        user_input = message.text

        if not u.thread:
            thread = assistant.client.beta.threads.create()
            u.thread = Thread.objects.create(thread_id=thread.id)
            u.save()
            logging.info(f'New thread created with ID: {thread.id}')

        thread_id = u.thread.thread_id
        logging.info(f'thread {thread_id} message: {user_input}')
        bot.send_chat_action(chat_id=chat_id, action='typing', timeout=10)
        response = assistant.get_answer(thread_id=thread_id, user_input=user_input, platform='telegram')
        try:
            bot.send_message(chat_id, response, parse_mode='Markdown')
        except BaseException:
            bot.send_message(chat_id, response, parse_mode='HTML')

    except BaseException as e:
        bot.send_message(chat_id, 'Something broken inside me. Please try again', parse_mode='HTML')
        raise e


@shared_task
def process_update(json_string):
    update = Update.de_json(json_string)
    if update:
        bot.process_new_updates([update])


class StartTelegramView(View):
    def post(self, request, *args, **kwargs):
        process_update.delay(json.loads(request.body))
        return JsonResponse({'ok': 'POST'})
