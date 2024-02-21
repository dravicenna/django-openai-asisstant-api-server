import json
import logging
import time

from celery import shared_task
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View

from assistant.celery import app
from hotel_bot import utils
from hotel_bot.assistant import assistant


@shared_task
def process_common_update(data):
    # data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')

    if not thread_id:
        logging.error('Error: Missing thread_id')
        # TODO check line below, about 400
        return JsonResponse({'error': 'Missing thread_id'}), 400

    logging.info(f'Received message: {user_input} for thread ID: {thread_id}')

    # response = assistant.get_answer(thread_id=thread_id, user_input=user_input, platform='webapp')
    response = '123'
    time.sleep(20)
    return response


class StartChatDefaultView(View):
    def get(self, request, *args, **kwargs):
        if utils.check_api_key(request):
            # TODO add to DB
            thread = assistant.client.beta.threads.create()
            logging.info(f'New thread created with ID: {thread.id}')
            return JsonResponse({'thread_id': thread.id})
        return HttpResponseBadRequest()


class ChatDefaultView(View):
    def get(self, request, *args, **kwargs):
        # if utils.check_api_key(request):
        if task_id := request.GET.get('task_id'):
            result = app.AsyncResult(task_id)
            if result.state == 'SUCCESS':
                return JsonResponse({'status': result.state, 'result': result.get()})
            return JsonResponse({'status': result.state})

    def post(self, request, *args, **kwargs):
        if utils.check_api_key(request):
            task = process_common_update.delay(json.loads(request.body))
            return JsonResponse({'task_id': task.id})
