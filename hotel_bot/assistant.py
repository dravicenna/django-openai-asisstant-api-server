import json
import logging
import time

import openai

from assistant.settings import ASSISTANT_ID, OPENAI_API_KEY
from hotel_bot import utils
from hotel_bot.tools import get_book_url


class AIAssistant:
    def __init__(self, id: str) -> None:
        self.id = id
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def get_answer(self, thread_id: str, user_input: str) -> str:
        try:
            message = self.client.beta.threads.messages.create(thread_id=thread_id, role='user', content=user_input)
        except openai.OpenAIError:
            # TODO catch error
            runs = self.client.beta.threads.runs.list(thread_id)
            self.client.beta.threads.runs.cancel(thread_id=thread_id, run_id='run_QlGVDKIV2GS2toHFs5tfuWZ9')
        # TODO save msg to db
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.id,
            additional_instructions=f'Today is {utils.get_date_string()}',
        )
        # This processes any possible action requests
        self.process_tool_calls(self.client, thread_id, run)

        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        try:
            response = messages.data[0].content[0].text.value  # type: ignore
        except IndexError as e:
            response = ''
            raise e
        logging.info(f'AI Response: {response}')
        return response

    def process_tool_calls(self, client, thread_id, run):
        """Process the actions that are initiated by the assistants API"""
        while True:
            run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run.status in ['completed', 'failed', 'expired', 'cancelled']:
                break
            elif run.status == 'requires_action' and run.required_action:
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    function_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logging.error(f'JSON decoding failed: {e.msg}. Input: {tool_call.function.arguments}')
                        arguments = {}  # Set to default value

                    # Use the function map from tool_data
                    if hasattr(get_book_url, function_name):
                        function_to_call = getattr(get_book_url, function_name)
                        output = function_to_call(arguments)
                        self.client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run.id,
                            tool_outputs=[{'tool_call_id': tool_call.id, 'output': json.dumps(output)}],
                        )
                    else:
                        logging.warning(f'Function {function_name} not found in tool data.')
            time.sleep(0.8)


assistant = AIAssistant(id=ASSISTANT_ID)
