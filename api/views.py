import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from assistant.settings import DEBUG
from hotel_bot import utils
from hotel_bot.assistant import assistant


def index(request):
    return render(request, 'api/index.html', {})


class StartView(View):
    def get(self, request, *args, **kwargs):
        if utils.check_api_key(request):
            # TODO add to DB
            thread = assistant.client.beta.threads.create()
            logging.info(f'New thread created with ID: {thread.id}')
            return JsonResponse({'thread_id': thread.id})


class ChatView(View):
    def post(self, request, *args, **kwargs):
        if DEBUG:
            ...
        else:
            ...
        if utils.check_api_key(request):
            data = request.json
            thread_id = data.get('thread_id')
            user_input = data.get('message', '')

            if not thread_id:
                logging.error('Error: Missing thread_id')
                # TODO check line below, about 400
                return JsonResponse({'error': 'Missing thread_id'}), 400

            logging.info(f'Received message: {user_input} for thread ID: {thread_id}')

            response = assistant.get_answer(thread_id=thread_id, user_input=user_input)

            return JsonResponse({'response': response})
